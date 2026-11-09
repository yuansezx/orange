"""角色 HTTP schema（Req / Resp）。

字段直接用 domain 值对象（RoleId / PermissionId / DeptId），经 `SingleValueObject`
统一裸值出入、OpenAPI 展示为 string（id 带 format: uuid）。
"""
from pydantic import BaseModel, Field

from app.iam.application.role.dto import (
    CreateRoleIn,
    RoleDetailOut,
    RoleListItemOut,
    RoleOut,
)
from app.iam.application.user_role_assignment.dto import (
    GetRoleCandidatesIn,
    GetRoleMembersIn,
    RoleCandidateUserOut,
    RoleMemberOut,
)
from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum
from app.iam.domain.shared.value_objects import DeptId, PermissionId, UserId


class CreateRoleReq(CreateRoleIn):
    """创建角色请求——线格式同 DTO。"""


class UpdateRoleReq(BaseModel):
    """整体替换角色请求——id 来自路径、code 不可改；PUT 语义：传什么就设成什么（含权限/部门集）。"""
    name: str
    data_scope: DataScopeEnum
    description: str | None = None
    status: StatusEnum
    permission_ids: list[PermissionId]
    dept_ids: list[DeptId]


class RoleResp(RoleOut):
    """角色响应（含权限集 / 数据范围部门集）——列表与 `/{id}` 同 schema。"""


class RoleListItemResp(RoleListItemOut):
    """角色列表项响应——数据字段 + 审计（平铺）。"""


class RoleDetailResp(RoleDetailOut):
    """角色详情响应——数据字段 + 审计（平铺）。"""


class GetRoleMembersReq(GetRoleMembersIn):
    """角色成员只读查询参数——线格式同 DTO。"""


class RoleMemberResp(RoleMemberOut):
    """角色成员响应（用户信息 + 分配状态）。"""


class GetRoleCandidatesReq(GetRoleCandidatesIn):
    """角色成员候选查询参数——线格式同 DTO。"""


class RoleCandidateUserResp(RoleCandidateUserOut):
    """候选用户响应（含 selected 标记）。"""


class PatchRoleUsersReq(BaseModel):
    """角色成员管理（增量）：只改本次指定的关系。"""
    add_user_ids: list[UserId] = Field(default_factory=list)
    remove_user_ids: list[UserId] = Field(default_factory=list)
