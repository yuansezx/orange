from abc import ABC, abstractmethod


class PasswordHasherPort(ABC):
    @abstractmethod
    def hash_password(self,password: str) -> str:...

    @abstractmethod
    def verify_password(self,password: str, password_hashed: str) -> bool:...
