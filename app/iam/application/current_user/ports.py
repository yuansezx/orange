from abc import ABC, abstractmethod

from app.iam.domain.shared.value_objects import UserId


class TokenManagerPort(ABC):
    @abstractmethod
    async def authenticate(self, token: str) -> UserId:
        """验证 token，返回 user_id；无效/过期/被吊销则抛 InvalidTokenException。"""
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
