"""用户头像存储端口（业务级）。

对象存储本身是基础设施，但这里只暴露「头像」这一业务能力：业务层不关心
bucket / key / S3 细节；适配器负责映射到具体后端（本地目录 / S3 兼容存储）。

当前统一由**后端代理读写**，故不提供预签名 URL / 公开 URL；缺失对象返回 None，
意外 IO 错误按基础设施异常冒泡。
"""
from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.iam.domain.shared.value_objects import UserId


class StoredAvatar(BaseModel):
    """读取到的头像：内容 + MIME 类型（后端代理时可据此设置 Content-Type）。"""
    data: bytes
    content_type: str


class AvatarStoragePort(ABC):
    @abstractmethod
    async def ensure_ready(self) -> None:
        """确保存储容器存在（S3 bucket / 本地目录）；启动时调用，幂等。"""
        ...

    @abstractmethod
    async def save(self, user_id: UserId, data: bytes, content_type: str) -> str:
        """保存头像并返回对象 key；key 由适配器生成（按用户分目录）。"""
        ...

    @abstractmethod
    async def load(self, key: str) -> StoredAvatar | None:
        """读取头像；不存在返回 None。"""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """删除头像；不存在视为成功（幂等）。"""
        ...
