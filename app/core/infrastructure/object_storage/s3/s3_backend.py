"""对象存储后端：S3 兼容服务（RustFS / MinIO / SeaweedFS / AWS S3）。

由 core 对象存储门面调用：`init` 接收该 backend 负责的连接子集
（{连接名: 连接参数}），为每个连接建一个 client 并返回；`close` 统一释放。
provider 差异（rustfs / aws 等）由业务侧 adapter 处理。
"""
from contextlib import AsyncExitStack
from typing import Any

from aiobotocore.session import get_session
from botocore.config import Config

_clients: dict[str, Any] = {}
_stack: AsyncExitStack | None = None


def _client_kwargs(options: dict) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        'region_name': options.get('region', 'us-east-1'),
        'config': Config(
            signature_version='s3v4',
            s3={
                'addressing_style': 'path' if options.get('path_style', True) else 'virtual',
            },
            retries={'max_attempts': 3},
            connect_timeout=5,
            read_timeout=30,
        ),
    }
    if options.get('endpoint_url'):
        kwargs['endpoint_url'] = options['endpoint_url']
    if options.get('access_key'):
        kwargs['aws_access_key_id'] = options['access_key']
    if options.get('secret_key'):
        kwargs['aws_secret_access_key'] = options['secret_key']
    return kwargs


async def init(connections: dict[str, dict]) -> dict[str, Any]:
    global _clients, _stack
    if _stack is not None:
        raise RuntimeError('对象存储已初始化')

    session = get_session()
    stack = AsyncExitStack()
    try:
        for name, options in connections.items():
            client = await stack.enter_async_context(
                session.create_client('s3', **_client_kwargs(options))
            )
            _clients[name] = client
    except Exception:
        _clients = {}
        await stack.aclose()
        raise
    _stack = stack
    return dict(_clients)


async def close() -> None:
    global _clients, _stack
    if _stack is not None:
        await _stack.aclose()
    _clients = {}
    _stack = None
