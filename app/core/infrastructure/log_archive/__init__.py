"""日志冷归档门面：构建 worker 交给 background 门面，并提供手动触发用的 controller。

写侧（core）只负责扫描/搬运；读侧（monitor）自己读同一对象存储。
"""
from app.core.infrastructure.log_archive.object_storage import ObjectStorageLogSink
from app.core.infrastructure.log_archive.ports import LogSinkPort
from app.core.infrastructure.log_archive.worker import LogArchiveWorker
from app.core.infrastructure.settings import CORE_SETTINGS, LogArchiveConfig

_worker: LogArchiveWorker | None = None


def _build_sink(config: LogArchiveConfig) -> LogSinkPort:
    if config.backend == 'object_storage':
        return ObjectStorageLogSink(connection=config.connection)
    raise RuntimeError(f'不支持的日志归档 backend：{config.backend}')


def build_log_archive(active_files: tuple[str, ...]) -> LogArchiveWorker | None:
    """按配置构建归档任务；未启用返回 None。未知 backend / 未配对象存储会直接抛错。"""
    global _worker
    archive = CORE_SETTINGS.logs.archive
    if archive is None or not archive.enabled:
        return None
    _worker = LogArchiveWorker(
        logs_dir=CORE_SETTINGS.logs.dir,
        active_files=active_files,
        instance=CORE_SETTINGS.logs.instance,
        sink=_build_sink(archive),
        interval_seconds=archive.interval_seconds,
        cold_after_seconds=archive.cold_after_seconds,
    )
    return _worker


def get_log_archive_controller() -> LogArchiveWorker | None:
    """供手动触发（monitor）；未启用时为 None。"""
    return _worker


def trigger_log_archive() -> bool:
    """手动触发一次归档（命令不是事件）；未启用返回 False。"""
    controller = get_log_archive_controller()
    if controller is None:
        return False
    controller.trigger()
    return True
