from abc import ABC, abstractmethod

from app.core.domain.ports import IdProviderPort
from app.iam.domain.shared.value_objects import UserId


class PasswordHasherPort(ABC):
    @abstractmethod
    def hash_password(self,password: str) -> str:...

    @abstractmethod
    def verify_password(self,password: str, password_hashed: str) -> bool:...

class UserIdProviderPort(IdProviderPort[UserId]):
    pass