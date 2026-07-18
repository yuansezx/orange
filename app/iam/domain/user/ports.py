from abc import ABC, abstractmethod

from app.core.domain.ports import IdProvider
from app.iam.domain.shared.value_objects import UserId


class PasswordHasher(ABC):
    @abstractmethod
    def hash_password(self,password: str) -> str:...

    @abstractmethod
    def verify_password(self,password: str, password_hashed: str) -> bool:...

class UserIdProvider(IdProvider[UserId]):
    pass