"""对象存储门面（与 cache / persistence 同构）。

core 按 `core.object_storage.connections` 的**命名连接**管理客户端生命周期：启动时
按连接的 `backend` 分组，每组动态导入一次后端（object_storage/{backend}/{backend}_backend.py），
一次初始化该组的全部连接，并统一持有各连接的 client。

未配置时不启动；`get_object_storage_client()` 在被实际使用时才抛错。
这里只管理“连接”；具体业务（头像、产物等）由各模块的 adapter 基于 port 实现。
"""
from importlib import import_module
from typing import Any

from loguru import logger

from app.core.infrastructure.settings import CORE_SETTINGS

# 连接名 → client；由 start_object_storage 一次性填充，core 统一持有
_clients: dict[str, Any] = {}
# backend 名 → 后端模块；仅用于关闭
_backends: dict[str, Any] = {}


def is_object_storage_configured() -> bool:
    return CORE_SETTINGS.object_storage is not None


def _load_backend(backend: str):
    return import_module(
        f'app.core.infrastructure.object_storage.{backend}.{backend}_backend'
    )


def _group_by_backend(connections: dict) -> dict[str, list[str]]:
    """按连接声明的 backend 分组；缺 backend 视为配置错误（fail-fast）。"""
    groups: dict[str, list[str]] = {}
    for name, options in connections.items():
        backend = options.get('backend')
        if not backend:
            raise RuntimeError(f'对象存储连接缺少 backend：{name}')
        groups.setdefault(backend, []).append(name)
    return groups


async def start_object_storage() -> None:
    if not is_object_storage_configured():
        logger.info('未配置 core.object_storage，跳过对象存储初始化')
        return
    connections = CORE_SETTINGS.object_storage.connections
    if not connections:
        raise RuntimeError('core.object_storage.connections 为空')
    try:
        for backend, names in _group_by_backend(connections).items():
            module = _load_backend(backend)
            clients = await module.init({name: connections[name] for name in names})
            _clients.update(clients)
            _backends[backend] = module
    except Exception:
        await stop_object_storage()
        raise
    logger.info('对象存储初始化完成：{}', ', '.join(connections))


async def stop_object_storage() -> None:
    for module in _backends.values():
        await module.close()
    _backends.clear()
    _clients.clear()


def get_object_storage_client(connection: str = 'default') -> Any:
    """取指定命名连接的 client；连接不存在或未启动时抛错。"""
    client = _clients.get(connection)
    if client is None:
        raise RuntimeError(f'对象存储连接未配置或未启动：{connection}')
    return client


def _connection_options(connection: str) -> dict:
    cfg = CORE_SETTINGS.object_storage
    if cfg is None:
        raise RuntimeError('缺少 core.object_storage 配置')
    options = cfg.connections.get(connection)
    if options is None:
        raise RuntimeError(f'对象存储连接未配置：{connection}')
    if not options.get('backend'):
        raise RuntimeError(f'对象存储连接缺少 backend：{connection}')
    return options


def get_object_storage_backend(connection: str = 'default') -> str:
    """取连接声明的 backend（实现）；组合根据此决定 adapter 的兜底范围。"""
    return _connection_options(connection)['backend']


def get_object_storage_provider(connection: str = 'default') -> str:
    """取连接的 provider（供业务侧选择 adapter）；缺省等于 backend。"""
    options = _connection_options(connection)
    return options.get('provider') or options['backend']
