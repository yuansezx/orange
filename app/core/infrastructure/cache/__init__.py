"""缓存门面（与 persistence 门面同构）。

core 通过本包管理缓存客户端生命周期；具体后端由 core.cache.backend 动态解析
（cache/{backend}/{backend}_backend.py）。未配置 core.cache 时不启动，
get_cache() 在被实际使用时才抛错。
"""
from importlib import import_module

from loguru import logger

from app.core.infrastructure.settings import CORE_SETTINGS


def _load_backend():
    cache = CORE_SETTINGS.cache
    if cache is None:
        raise RuntimeError('缺少 core.cache 配置')
    return import_module(f'app.core.infrastructure.cache.{cache.backend}.{cache.backend}_backend')


def is_cache_configured() -> bool:
    return CORE_SETTINGS.cache is not None


async def start_cache() -> None:
    if not is_cache_configured():
        logger.info('未配置 core.cache，跳过缓存初始化')
        return
    await _load_backend().init(CORE_SETTINGS.cache)
    logger.info('缓存初始化完成。')


async def stop_cache() -> None:
    if is_cache_configured():
        await _load_backend().close()


def get_cache():
    """返回缓存客户端（当前实现为 redis-py 的 asyncio 客户端）。"""
    return _load_backend().get_client()
