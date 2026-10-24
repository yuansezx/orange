from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel

from app.core.exceptions import InfrastructureBaseException
from app.iam.domain.shared.value_objects import UserId


class SessionMeta(BaseModel):
    """登录会话元数据（写入会话白名单）。"""
    login_at: datetime
    expires_at: datetime
    login_ip: str | None = None
    login_user_agent: str | None = None


class AuthenticatedSession(BaseModel):
    """认证后的会话标识（不暴露 JWT 术语）。"""
    user_id: UserId
    session_id: str


class SessionInfo(SessionMeta):
    """在线会话视图（读取会话白名单）。"""
    user_id: UserId
    session_id: str


class SessionVerificationException(InfrastructureBaseException):
    """会话校验失败——**技术中立**（不预判业务结论）。

    基础层（适配器）只负责把 jwt 库异常翻到这里；「无效令牌」这个业务结论
    由应用层翻成 InvalidTokenException。端口私有契约类型，与端口同处。
    """


class SessionManagerPort(ABC):
    @abstractmethod
    async def create(self, user_id: UserId, ttl: int, *, meta: SessionMeta) -> str:
        """创建会话并返回 access token（ttl 秒）。"""
        ...

    @abstractmethod
    async def authenticate(self, token: str) -> AuthenticatedSession:
        """验证 token 并返回会话标识；失败抛 SessionVerificationException。"""
        ...

    @abstractmethod
    async def get_all(self, user_id: UserId | None = None) -> list[SessionInfo]:
        """列出会话；`user_id=None` 表示全部在线会话。"""
        ...

    @abstractmethod
    async def revoke(self, user_id: UserId, session_ids: set[str]) -> int:
        """吊销该用户的指定会话；返回实际移除的会话数。"""
        ...

    @abstractmethod
    async def revoke_users(self, user_ids: set[UserId]) -> int:
        """吊销多个用户的全部会话；返回实际移除的 key 数。"""
        ...
