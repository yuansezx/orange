import sys
from importlib import import_module

from loguru import logger

from app.core.infrastructure import background
from app.core.infrastructure.event_bus_impl import EventBusImpl
from app.core.infrastructure.event_relay import EventRelay, LocalEventTransport
from app.core.infrastructure.log_archive import (
    build_log_archive,
    get_log_archive_controller,
    trigger_log_archive,
)
from app.core.infrastructure.cache import start_cache, stop_cache
from app.core.infrastructure.object_storage import start_object_storage, stop_object_storage
from app.core.infrastructure.persistence import start_persistence, stop_persistence
from app.core.infrastructure.settings import CORE_SETTINGS


# 活跃日志文件名：loguru 正在写、归档任务不能碰的文件
APP_LOG = 'app.log'
ERROR_LOG = 'error.log'
ACTIVE_LOG_FILES = (APP_LOG, ERROR_LOG)


# 初始化loguru
def init_logger():
    CORE_SETTINGS.logs_dir.mkdir(parents=True, exist_ok=True)
    # 移除原生控制台输出
    logger.remove()
    # 添加控制台输出
    logger.add(sys.stderr, colorize=True, level="INFO",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}  - {message}")
    # 所有模块的log写入app.log
    logger.add(CORE_SETTINGS.logs_dir / APP_LOG,
               level='INFO',
               format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}  - {message}',
               encoding='utf-8',
               rotation=CORE_SETTINGS.logs.rotation,
               retention=CORE_SETTINGS.logs.retention,
               enqueue=True  # 异步
               )
    # error级别log单独写入error.log
    logger.add(CORE_SETTINGS.logs_dir / ERROR_LOG,
               level='ERROR',
               format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}  - {message}',
               encoding='utf-8',
               rotation=CORE_SETTINGS.logs.rotation,
               retention=CORE_SETTINGS.logs.retention,
               enqueue=True)
    logger.info('日志初始化完成。')

# 事件总线 / relay
_event_bus: EventBusImpl | None = None
_event_relay: EventRelay | None = None


def get_event_bus() -> EventBusImpl:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBusImpl()
    return _event_bus

async def start():
    """应用启动：日志 → 持久化 → 缓存 → 对象存储 → 模块钩子 → 后台任务 → 事件 relay。"""
    init_logger()
    await start_persistence()
    await start_cache()
    await start_object_storage()
    await _run_module_bootstraps()
    # 模块 bootstrap 阶段完成后台任务注册，此处统一启动
    # 日志冷归档是 core 自己的自主任务：在这里手动构建并注册（不走模块 bootstrap）
    archive_worker = build_log_archive(ACTIVE_LOG_FILES)
    if archive_worker is not None:
        background.register(archive_worker)
    await background.start_all()
    # relay 在模块 bootstrap 之后启动：此时 outbox store 与订阅者已登记
    await _start_event_relay()


async def stop():
    """应用关闭：先停 relay 与后台任务，再释放对象存储、缓存与持久化资源。"""
    await _stop_event_relay()
    await background.stop_all()
    await stop_object_storage()
    await stop_cache()
    await stop_persistence()


async def _start_event_relay() -> None:
    global _event_relay
    bus = get_event_bus()
    _event_relay = EventRelay(bus, [LocalEventTransport(bus)], CORE_SETTINGS.events)
    await _event_relay.start()


async def _stop_event_relay() -> None:
    global _event_relay
    if _event_relay is not None:
        await _event_relay.stop()
        _event_relay = None


async def _run_module_bootstraps() -> None:
    """按 core.modules 依次调用各模块的 `app.{模块}.bootstrap()`。

    模块未提供 bootstrap 模块则跳过（钩子可选）。core 只认约定，不认识具体模块。
    """
    for name in CORE_SETTINGS.modules:
        path = f'app.{name}.bootstrap'
        try:
            module = import_module(path)
        except ModuleNotFoundError as e:
            if e.name == path:
                logger.debug('模块 {} 未提供 bootstrap，跳过', name)
                continue
            raise
        hook = getattr(module, 'bootstrap', None)
        if hook is not None:
            logger.info('运行模块启动钩子：{}', path)
            await hook()