from pydantic import BaseModel, Field

from app.iam.application.common.dto import AuditOut, DeptRefOut
from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum
from app.iam.domain.shared.value_objects import DeptId, PermissionId, RoleId


class CreateRoleIn(BaseModel):
    code: str
    name: str
    data_scope: DataScopeEnum
    description: str | None = None
    permission_ids: list[PermissionId]
    dept_ids: list[DeptId]


class UpdateRoleIn(BaseModel):
    """整体替换角色（PUT 语义）：传什么就设成什么，含权限集 / 数据范围部门集。"""
    id: RoleId
    name: str
    data_scope: DataScopeEnum
    description: str | None = None
    status: StatusEnum
    permission_ids: list[PermissionId]
    dept_ids: list[DeptId]


class RoleOut(BaseModel):
    id: RoleId
    code: str
    name: str
    data_scope: DataScopeEnum
    status: StatusEnum
    description: str | None = None
    permission_ids: list[PermissionId] = Field(default_factory=list)
    dept_ids: list[DeptId] = Field(default_factory=list)


class RoleDetailOut(RoleOut, AuditOut):
    """角色详情——数据字段 + 审计（平铺）+ 数据范围部门引用（名字+路径）。"""
    dept_refs: list[DeptRefOut] = Field(default_factory=list)
