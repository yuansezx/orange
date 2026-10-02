from abc import ABC, abstractmethod

from app.iam.domain.shared.value_objects import UserId


class TokenManagerPort(ABC):
    @abstractmethod
    def authenticate(self, token: str) -> UserId:
        """验证token,返回user_id"""
        ...

    @abstractmethod
    def create(self, user_id: UserId, ttl: int) -> str:
        ...

    @abstractmethod
    def revoke(self, token: str) -> None:
        ...

    @abstractmethod
    def revoke_all(self, user_id: UserId) -> None:
        ...
