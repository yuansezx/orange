"""缓存后端：redis-py asyncio。"""
from redis.asyncio import Redis

from app.core.infrastructure.settings import CacheConfig

_client: Redis | None = None


def _build_client(cfg: CacheConfig) -> Redis:
    o = cfg.options
    auth = f':{o["password"]}@' if o.get('password') else ''
    url = f'redis://{auth}{o.get("host", "127.0.0.1")}:{o.get("port", 6379)}/{o.get("db", 0)}'
    return Redis.from_url(url, decode_responses=True)


async def init(cfg: CacheConfig) -> None:
    global _client
    _client = _build_client(cfg)


async def close() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def get_client() -> Redis:
    if _client is None:
        raise RuntimeError('缓存未配置或未启动')
    return _client
