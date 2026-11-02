"""对象存储门面（与 cache / persistence 同构）。

core 按 `core.object_storage.backend` 动态解析后端；后端负责按 `options` 里的
**命名连接**建立/关闭 client。未配置时不启动，`get_object_storage_client()` 在
被实际使用时才抛错。

这里只管理“连接”；具体业务（头像等）由各模块的 adapter 基于 port 实现。
"""
from importlib import import_module
from typing import Any

from loguru import logger

from app.core.infrastructure.settings import CORE_SETTINGS


def _load_backend():
    cfg = CORE_SETTINGS.object_storage
    if cfg is None:
        raise RuntimeError('缺少 core.object_storage 配置')
    return import_module(
        f'app.core.infrastructure.object_storage.{cfg.backend}.{cfg.backend}_backend'
    )


def is_object_storage_configured() -> bool:
    return CORE_SETTINGS.object_storage is not None


async def start_object_storage() -> None:
    if not is_object_storage_configured():
        logger.info('未配置 core.object_storage，跳过对象存储初始化')
        return
    await _load_backend().init(CORE_SETTINGS.object_storage)
    logger.info('对象存储初始化完成。')


async def stop_object_storage() -> None:
    if is_object_storage_configured():
        await _load_backend().close()


def get_object_storage_client(connection: str = 'default') -> Any:
    """取指定命名连接的 client；连接不存在时抛错。"""
    return _load_backend().get_client(connection)


def get_object_storage_provider(connection: str = 'default') -> str:
    """取连接的 provider（供业务侧选择 adapter）；缺省 s3。"""
    cfg = CORE_SETTINGS.object_storage
    if cfg is None:
        raise RuntimeError('缺少 core.object_storage 配置')
    options = cfg.options.get(connection)
    if options is None:
        raise RuntimeError(f'对象存储连接未配置：{connection}')
    return options.get('provider', 's3')
