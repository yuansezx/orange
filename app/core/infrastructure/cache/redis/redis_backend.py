"""缓存后端：redis-py asyncio。

由 core 缓存门面调用：`init` 接收该 backend 负责的连接子集（{连接名: 连接参数}），
为每个连接建一个 client 并返回；`close` 统一释放。
"""
from typing import Any

from redis.asyncio import Redis

_clients: dict[str, Redis] = {}


def _build_client(options: dict) -> Redis:
    auth = f':{options["password"]}@' if options.get('password') else ''
    url = f'redis://{auth}{options.get("host", "127.0.0.1")}:{options.get("port", 6379)}/{options.get("db", 0)}'
    return Redis.from_url(url, decode_responses=True)


async def init(connections: dict[str, dict]) -> dict[str, Any]:
    global _clients
    if _clients:
        raise RuntimeError('redis 缓存已初始化')
    _clients = {name: _build_client(options) for name, options in connections.items()}
    return dict(_clients)


async def close() -> None:
    global _clients
    for client in _clients.values():
        await client.aclose()
    _clients = {}
