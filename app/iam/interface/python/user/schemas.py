"""iam 对外 Python API 的用户 schema。"""
from uuid import UUID

from pydantic import BaseModel


class UserRefResp(BaseModel):
    """批量用户引用（供其他模块展示创建人/操作人）。"""
    id: UUID
    username: str
    nickname: str
    avatar_url: str | None = None
