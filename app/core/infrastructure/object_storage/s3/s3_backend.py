"""对象存储后端：S3 兼容服务（RustFS / MinIO / SeaweedFS / AWS S3）。

core 只负责按命名连接建立并持有 client；provider 差异由业务侧 adapter 处理。
"""
from contextlib import AsyncExitStack
from typing import Any

from aiobotocore.session import get_session
from botocore.config import Config

from app.core.infrastructure.settings import ObjectStorageConfig

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


async def init(cfg: ObjectStorageConfig) -> None:
    global _clients, _stack
    if _stack is not None:
        raise RuntimeError('对象存储已初始化')
    if not cfg.options:
        raise ValueError('core.object_storage.options 为空')

    session = get_session()
    stack = AsyncExitStack()
    try:
        for name, options in cfg.options.items():
            client = await stack.enter_async_context(
                session.create_client('s3', **_client_kwargs(options))
            )
            _clients[name] = client
    except Exception:
        _clients = {}
        await stack.aclose()
        raise
    _stack = stack


async def close() -> None:
    global _clients, _stack
    if _stack is not None:
        await _stack.aclose()
    _clients = {}
    _stack = None


def get_client(connection: str = 'default') -> Any:
    if connection not in _clients:
        raise RuntimeError(f'对象存储连接未配置：{connection}')
    return _clients[connection]
