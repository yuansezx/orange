"""postgres 方言层：把连接配置拼成 tortoise 认的连接。

配置里只写 `{dialect, credentials}`（库名在 credentials 内），engine 由本层补齐——
DB 方言是这里的事，不该焊进业务配置。将来支持别的库，加 `tortoise/{dialect}/` 目录即可。
"""

ENGINE = 'tortoise.backends.asyncpg'


def build_connection(spec: dict) -> dict:
    """连接配置 → tortoise 连接（补 engine；凭据原样透传，含库名 `database`）。"""
    return {'engine': ENGINE, 'credentials': dict(spec['credentials'])}
