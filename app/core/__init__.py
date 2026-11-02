import sys
from importlib import import_module

from loguru import logger

from app.core.infrastructure.event_bus_impl import EventBusImpl
from app.core.infrastructure.event_relay import EventRelay, LocalEventTransport
from app.core.infrastructure.cache import start_cache, stop_cache
from app.core.infrastructure.object_storage import start_object_storage, stop_object_storage
from app.core.infrastructure.persistence import start_persistence, stop_persistence
from app.core.infrastructure.settings import CORE_SETTINGS


# 初始化loguru
def init_logger():
    CORE_SETTINGS.logs_dir.mkdir(parents=True, exist_ok=True)
    # 移除原生控制台输出
    logger.remove()
    # 添加控制台输出
    logger.add(sys.stderr, colorize=True, level="INFO",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}  - {message}")
    # 所有模块的log写入app.log
    logger.add(CORE_SETTINGS.logs_dir / 'app.log',
               level='INFO',
               format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}  - {message}',
               encoding='utf-8',
               enqueue=True  # 异步
               )
    # error级别log单独写入error.log
    logger.add(CORE_SETTINGS.logs_dir / 'error.log',
               level='ERROR',
               format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}  - {message}',
               encoding='utf-8',
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
    """应用启动：日志 → 持久化 → 缓存 → 对象存储 → 模块钩子 → 事件 relay。"""
    init_logger()
    await start_persistence()
    await start_cache()
    await start_object_storage()
    await _run_module_bootstraps()
    # relay 在模块 bootstrap 之后启动：此时 outbox store 与订阅者已登记
    await _start_event_relay()


async def stop():
    """应用关闭：先停 relay，再释放对象存储、缓存与持久化资源。"""
    await _stop_event_relay()
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