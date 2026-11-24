"""日志冷归档任务：扫描 loguru 轮转后的文件，交给 sink 送出，成功后删本地。"""
import asyncio
import time
from pathlib import Path

from loguru import logger

from app.core.infrastructure.log_archive.keys import build_key
from app.core.infrastructure.log_archive.ports import LogSinkPort


class LogArchiveWorker:
    """自主驱动的常驻任务（见 tmp/知识库/架构/后台任务.md）。

    - 只处理不在 active_files 里的文件（已轮转、已封口）；
    - 按 mtime 冷却，避免刚轮转时还在落盘；
    - 先送成功再删本地，失败留原地、下轮重试（key 由文件名派生，重传覆盖即幂等）。
    """

    def __init__(self, *, logs_dir: Path, active_files: tuple[str, ...],
                 instance: str, sink: LogSinkPort,
                 interval_seconds: float, cold_after_seconds: int) -> None:
        self._logs_dir = logs_dir
        self._active_files = set(active_files)
        self._instance = instance
        self._sink = sink
        self._interval = interval_seconds
        self._cold_after = cold_after_seconds
        self._task: asyncio.Task | None = None
        self._wakeup = asyncio.Event()
        self._failures: dict[Path, float] = {}

    async def start(self) -> None:
        await self._sink.ensure_ready()
        self._task = asyncio.create_task(self._run(), name='log-archive')

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    def trigger(self) -> None:
        """手动触发：唤醒一次（命令不是事件，不进事件总线）。"""
        self._wakeup.set()

    async def _run(self) -> None:
        while True:
            try:
                await self.run_once()
            except Exception:
                logger.exception('日志归档轮询失败')
            try:
                await asyncio.wait_for(self._wakeup.wait(), timeout=self._interval)
            except TimeoutError:
                pass
            self._wakeup.clear()

    async def run_once(self) -> None:
        now = time.time()
        for path in sorted(self._logs_dir.glob('*.log')):
            if path.name in self._active_files:
                continue
            try:
                mtime = path.stat().st_mtime
            except FileNotFoundError:
                continue
            if now - mtime < self._cold_after:
                continue
            if self._failures.get(path, 0) > now:
                continue
            try:
                await self._archive(path, mtime)
            except Exception:
                logger.exception('日志归档失败：{}', path.name)

    async def _archive(self, path: Path, mtime: float) -> None:
        key = build_key(self._instance, mtime, path.name)
        try:
            data = await asyncio.to_thread(path.read_bytes)
            await self._sink.put(key, data)
        except Exception:
            self._failures[path] = time.time() + 300
            raise
        self._failures.pop(path, None)
        try:
            path.unlink()
        except OSError:
            self._failures[path] = time.time() + 300
            logger.warning('日志已归档但删除本地失败：{}', path.name)
            return
        logger.info('日志已归档：{} -> {}', path.name, key)
