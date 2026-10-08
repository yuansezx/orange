from abc import ABC, abstractmethod

from app.core.exceptions import InfrastructureBaseException
from app.iam.domain.shared.value_objects import UserId


class TokenVerificationException(InfrastructureBaseException):
    """令牌校验失败——**技术中立**（不预判业务结论）。

    基础层（适配器）只负责把 jwt 库异常翻到这里；「无效令牌」这个业务结论
    由应用层翻成 InvalidTokenException。端口私有契约类型，与端口同处。
    """


class TokenManagerPort(ABC):
    @abstractmethod
    async def authenticate(self, token: str) -> UserId:
        """验证 token，返回 user_id；校验失败抛 TokenVerificationException。"""
        ...

    @abstractmethod
    async def create(self, user_id: UserId, ttl: int) -> str:
        """为用户签发令牌（ttl 秒）。"""
        ...

    @abstractmethod
    async def revoke(self, token: str) -> None:
        """吊销单个令牌（单端登出）。"""
        ...

    @abstractmethod
    async def revoke_all(self, user_id: UserId) -> None:
        """吊销该用户全部令牌（全端登出）。"""
        ...
