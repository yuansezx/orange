import re
from dataclasses import dataclass

from app.core.domain.value_objects import BaseEntityId, SingleValueObject
from app.iam.domain.shared.enums import DataScopeEnum


@dataclass(frozen=True)
class Phone(SingleValueObject[str]):
    def __post_init__(self):
        if not re.match(r'^1[3-9]\d{9}$', self.value):
            raise ValueError(f"手机号格式不正确: {self.value}")

    @property
    def masked(self) -> str:
        return self.value[:3] + "****" + self.value[-4:]


@dataclass(frozen=True)
class Email(SingleValueObject[str]):
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


@dataclass(frozen=True)
class ResourceId(BaseEntityId):
    pass


@dataclass(frozen=True)
class PermissionId(BaseEntityId):
    pass


@dataclass(frozen=True)
class RoleSummary:
    """角色的精简视图（供 CurrentUser 缓存展示 / 可选角色码检查；非完整聚合）。"""
    id: RoleId
    code: str
    name: str


@dataclass(frozen=True)
class DataScopeSpec:
    """数据范围**规约**（selection）——解析结果，供仓储/查询**翻译**成过滤条件（不推导政策）。"""
    kind: DataScopeEnum
    dept_ids: frozenset[DeptId] = frozenset()   # CUSTOM 的指定部门（DEPT_AND_CHILD 展开后和DEPT的dept_id也放这）
    actor_id: UserId | None = None              # SELF：本人 id

    @classmethod
    def all(cls) -> 'DataScopeSpec':
        return cls(DataScopeEnum.ALL)

    @classmethod
    def own(cls, actor_id: UserId) -> 'DataScopeSpec':
        return cls(DataScopeEnum.SELF, actor_id=actor_id)

    @classmethod
    def custom(cls, dept_ids) -> 'DataScopeSpec':
        return cls(DataScopeEnum.CUSTOM, dept_ids=frozenset(dept_ids))
