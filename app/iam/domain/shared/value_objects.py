import re
from dataclasses import dataclass

from app.core.domain.value_objects import BaseEntityId


@dataclass(frozen=True)
class Phone:
    value: str

    def __post_init__(self):
        if not re.match(r'^1[3-9]\d{9}$', self.value):
            raise ValueError(f"手机号格式不正确: {self.value}")

    @property
    def masked(self) -> str:
        return self.value[:3] + "****" + self.value[-4:]


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', self.value):
            raise ValueError(f"邮箱格式不正确: {self.value}")

    @property
    def masked(self) -> str:
        local, domain = self.value.split("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"


@dataclass(frozen=True)
class UserId(BaseEntityId):
    pass


@dataclass(frozen=True)
class RoleId(BaseEntityId):
    pass


@dataclass(frozen=True)
class DeptId(BaseEntityId):
    pass

@dataclass(frozen=True)
class UserRoleId(BaseEntityId):
    pass
