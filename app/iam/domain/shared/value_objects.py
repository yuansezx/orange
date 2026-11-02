import re
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.domain.value_objects import BaseEntityId, SingleValueObject
from app.iam.domain.shared.enums import DataScopeEnum


class Phone(SingleValueObject[str]):
    @field_validator('root')
    @classmethod
    def _validate(cls, value: str) -> str:
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise ValueError(f"手机号格式不正确: {value}")
        return value

    @property
    def masked(self) -> str:
        return self.root[:3] + "****" + self.root[-4:]


class Email(SingleValueObject[str]):
    @field_validator('root')
    @classmethod
    def _validate(cls, value: str) -> str:
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', value):
            raise ValueError(f"邮箱格式不正确: {value}")
        return value

    @property
    def masked(self) -> str:
        local, domain = self.root.split("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"


class UserId(BaseEntityId):
    pass


class RoleId(BaseEntityId):
    pass


class DeptId(BaseEntityId):
    pass


class UserRoleId(BaseEntityId):
    pass


class ResourceId(BaseEntityId):
    pass


class PermissionId(BaseEntityId):
    pass


class RoleSummary(BaseModel):
    """角色的精简视图（供 CurrentUser 缓存展示 / 可选角色码检查；非完整聚合）。"""
    model_config = ConfigDict(frozen=True)

    id: RoleId
    code: str
    name: str


class DataScopeSpec(BaseModel):
    """数据范围**规约**（selection）——解析结果，供仓储/查询**翻译**成过滤条件（不推导政策）。"""
    model_config = ConfigDict(frozen=True)

    kind: DataScopeEnum
    dept_ids: frozenset[DeptId] = frozenset()   # CUSTOM 的指定部门（DEPT_AND_CHILD 展开后和DEPT的dept_id也放这）
    actor_id: UserId | None = None              # SELF：本人 id

    @classmethod
    def all(cls) -> Self:
        return cls(kind=DataScopeEnum.ALL)

    @classmethod
    def own(cls, actor_id: UserId) -> Self:
        return cls(kind=DataScopeEnum.SELF, actor_id=actor_id)

    @classmethod
    def custom(cls, dept_ids) -> Self:
        return cls(kind=DataScopeEnum.CUSTOM, dept_ids=frozenset(dept_ids))
