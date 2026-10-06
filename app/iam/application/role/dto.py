from pydantic import BaseModel, Field

from app.iam.domain.role.enums import DataScopeEnum
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, PermissionId, RoleId


class CreateRoleIn(BaseModel):
    code: str
    name: str
    data_scope: DataScopeEnum
    description: str | None = None
    permission_ids: list[PermissionId] | None = None
    dept_ids: list[DeptId] | None = None


class UpdateRoleIn(BaseModel):
    id: RoleId
    name: str | None = None
    data_scope: DataScopeEnum | None = None
    description: str | None = None
    status: StatusEnum | None = None


class SetRolePermissionsIn(BaseModel):
    role_id: RoleId
    permission_ids: list[PermissionId] = Field(default_factory=list)


class SetRoleDeptsIn(BaseModel):
    role_id: RoleId
    dept_ids: list[DeptId] = Field(default_factory=list)


class RoleOut(BaseModel):
    id: RoleId
    code: str
    name: str
    data_scope: DataScopeEnum
    status: StatusEnum
    description: str | None = None


class RoleDetailOut(RoleOut):
    permission_ids: list[PermissionId] = Field(default_factory=list)
    dept_ids: list[DeptId] = Field(default_factory=list)
