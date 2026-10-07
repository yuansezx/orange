import sys
from importlib import import_module

from loguru import logger

from app.core.domain.event_bus import EventBus
from app.core.infrastructure.event_bus_impl import EventBusMemoryImpl
from app.core.infrastructure.cache import start_cache, stop_cache
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

# 事件总线
_event_bus: EventBus | None = None
def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBusMemoryImpl()
    return _event_bus

async def start():
    """应用启动：日志 → 持久化（迁移 + ORM 初始化）→ 缓存 → 各模块启动钩子。"""
    init_logger()
    await start_persistence()
    await start_cache()
    await _run_module_bootstraps()


async def stop():
    """应用关闭：释放缓存与持久化资源。"""
    await stop_cache()
    await stop_persistence()


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