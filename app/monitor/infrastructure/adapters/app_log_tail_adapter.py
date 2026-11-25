"""实时应用日志适配器：tail 本地活跃文件，产出 SSE data 行。

只读 app.log / error.log，不碰归档；rotation 时检测到文件变小就重置 offset。
"""
import asyncio
import codecs
import time
from collections.abc import AsyncIterator
from pathlib import Path

from app.core import APP_LOG, ERROR_LOG
from app.monitor.application.app_log.ports import AppLogTailPort

_FILES = {'app': APP_LOG, 'error': ERROR_LOG}
_INITIAL_LINES = 200
_INITIAL_BYTES = 128 * 1024
_POLL_SECONDS = 1.0
_HEARTBEAT_SECONDS = 20.0


class AppLogTailAdapter(AppLogTailPort):
    def __init__(self, logs_dir: Path) -> None:
        self._logs_dir = logs_dir

    def stream(self, file: str) -> AsyncIterator[str]:
        return self._stream(file)

    async def _stream(self, file: str) -> AsyncIterator[str]:
        path = self._logs_dir / _FILES[file]
        for line in await asyncio.to_thread(self._initial_lines, path):
            yield _data(line)
        offset = await asyncio.to_thread(self._size, path)
        decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
        buffer = ''
        last_sent = time.monotonic()
        while True:
            await asyncio.sleep(_POLL_SECONDS)
            try:
                size = path.stat().st_size
            except FileNotFoundError:
                continue
            if size < offset:
                offset = 0
                decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
                buffer = ''
                yield 'event: rotated\ndata: 日志已轮转\n\n'
            if size > offset:
                data = await asyncio.to_thread(self._read_from, path, offset)
                offset += len(data)
                buffer += decoder.decode(data)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    yield _data(line.rstrip('\r'))
                last_sent = time.monotonic()
            elif time.monotonic() - last_sent >= _HEARTBEAT_SECONDS:
                yield ': ping\n\n'
                last_sent = time.monotonic()

    @staticmethod
    def _size(path: Path) -> int:
        try:
            return path.stat().st_size
        except FileNotFoundError:
            return 0

    @staticmethod
    def _initial_lines(path: Path) -> list[str]:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return []
        with path.open('rb') as f:
            f.seek(max(0, size - _INITIAL_BYTES))
            data = f.read()
        lines = data.decode('utf-8', errors='replace').splitlines()
        return lines[-_INITIAL_LINES:]

    @staticmethod
    def _read_from(path: Path, offset: int) -> bytes:
        try:
            with path.open('rb') as f:
                f.seek(offset)
                return f.read()
        except FileNotFoundError:
            return b''


def _data(line: str) -> str:
    return f'data: {line}\n\n'
