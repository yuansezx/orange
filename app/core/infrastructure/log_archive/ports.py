"""日志归档目的地端口（基础设施内部接缝：filesystem / object_storage / http 切换）。"""
from typing import Protocol


class LogSinkPort(Protocol):
    """把归档文件送到某处；backend 差异只在实现里。"""

    async def ensure_ready(self) -> None: ...

    async def put(self, key: str, data: bytes) -> None: ...
