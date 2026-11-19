"""缓存门面（与 persistence / object_storage 同构）。

core 按 `core.cache.connections` 的**命名连接**管理客户端生命周期：启动时按连接的
`backend` 分组，每组动态导入一次后端（cache/{backend}/{backend}_backend.py），
一次初始化该组的全部连接，并统一持有各连接的 client。

未配置 core.cache 时不启动；`get_cache()` 在被实际使用时才抛错。
连接名是 dev/ops 的契约，模块只按名字取，不感知 backend。
"""
from importlib import import_module
from typing import Any

from loguru import logger

from app.core.infrastructure.settings import CORE_SETTINGS

# 连接名 → client；由 start_cache 一次性填充，core 统一持有
_clients: dict[str, Any] = {}
# backend 名 → 后端模块；仅用于关闭
_backends: dict[str, Any] = {}


def is_cache_configured() -> bool:
    return CORE_SETTINGS.cache is not None


def _load_backend(backend: str):
    return import_module(f'app.core.infrastructure.cache.{backend}.{backend}_backend')


def _group_by_backend(connections: dict) -> dict[str, list[str]]:
    """按连接声明的 backend 分组；缺 backend 视为配置错误（fail-fast）。"""
    groups: dict[str, list[str]] = {}
    for name, options in connections.items():
        backend = options.get('backend')
        if not backend:
            raise RuntimeError(f'缓存连接缺少 backend：{name}')
        groups.setdefault(backend, []).append(name)
    return groups


async def start_cache() -> None:
    if not is_cache_configured():
        logger.info('未配置 core.cache，跳过缓存初始化')
        return
    connections = CORE_SETTINGS.cache.connections
    if not connections:
        raise RuntimeError('core.cache.connections 为空')
    try:
        for backend, names in _group_by_backend(connections).items():
            module = _load_backend(backend)
            clients = await module.init({name: connections[name] for name in names})
            _clients.update(clients)
            _backends[backend] = module
    except Exception:
        await stop_cache()
        raise
    logger.info('缓存初始化完成：{}', ', '.join(connections))


async def stop_cache() -> None:
    for module in _backends.values():
        await module.close()
    _backends.clear()
    _clients.clear()


def get_cache(connection: str = 'default') -> Any:
    """返回指定命名连接的缓存客户端（实现由该连接的 backend 决定）。"""
    client = _clients.get(connection)
    if client is None:
        raise RuntimeError(f'缓存连接未配置或未启动：{connection}')
    return client


def get_cache_provider(connection: str = 'default') -> str:
    """取连接的 provider（供业务侧选择 adapter）；缺省等于 backend。

    同协议出现多种服务（valkey / keydb 等）时，在连接里加 `provider`，
    组合根即可按 provider 注册不同 adapter。
    """
    cfg = CORE_SETTINGS.cache
    if cfg is None:
        raise RuntimeError('缺少 core.cache 配置')
    options = cfg.connections.get(connection)
    if options is None:
        raise RuntimeError(f'缓存连接未配置：{connection}')
    backend = options.get('backend')
    if not backend:
        raise RuntimeError(f'缓存连接缺少 backend：{connection}')
    return options.get('provider') or backend
