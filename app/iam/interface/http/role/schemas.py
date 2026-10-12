"""角色 HTTP schema（Req / Resp）。

字段直接用 domain 值对象（RoleId / PermissionId / DeptId），经 `SingleValueObject`
统一裸值出入、OpenAPI 展示为 string（id 带 format: uuid）。
"""
from pydantic import BaseModel, Field

from app.iam.application.role.dto import CreateRoleIn, RoleDetailOut, RoleOut
from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum
from app.iam.domain.shared.value_objects import DeptId, PermissionId


class CreateRoleReq(CreateRoleIn):
    """创建角色请求——线格式同 DTO。"""


class UpdateRoleReq(BaseModel):
    """更新角色请求——id 来自路径，故不含 id；code 不可改。"""
    name: str | None = None
    data_scope: DataScopeEnum | None = None
    description: str | None = None
    status: StatusEnum | None = None


class SetRolePermissionsReq(BaseModel):
    permission_ids: list[PermissionId] = Field(default_factory=list)


class SetRoleDeptsReq(BaseModel):
    dept_ids: list[DeptId] = Field(default_factory=list)


class RoleResp(RoleOut):
    """角色响应——线格式同 DTO。"""


class RoleDetailResp(RoleDetailOut):
    """角色详情响应（含权限集 / 数据范围部门集）。"""
