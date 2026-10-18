"""用户 HTTP schema（Req / Resp）。

字段直接用 domain 值对象（Email / Phone / DeptId），经 `SingleValueObject`
统一裸值出入、OpenAPI 展示为 string（id 带 format: uuid），无需重复写 pattern。
"""
from pydantic import BaseModel

from app.iam.application.user.dto import (
    CreateUserIn,
    GetUsersIn,
    UserDetailOut,
    UserListItemOut,
    UserOut,
)
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, Email, Phone, RoleId


class CreateUserReq(CreateUserIn):
    """创建用户请求——线格式同 DTO。"""


class UpdateUserReq(BaseModel):
    """更新用户请求——id 来自路径，故不含 id。"""
    nickname: str
    email: Email | None = None
    phone: Phone | None = None
    status: StatusEnum
    description: str | None = None
    role_ids: list[RoleId] | None = None
    dept_id: DeptId | None = None


class GetUsersReq(GetUsersIn):
    """用户列表查询参数——线格式同 DTO（时间 start/end 各自可选）。"""


class UserResp(UserOut):
    """用户响应——数据字段 + 生命周期时间（**不含 password_hash**）。"""


class UserListItemResp(UserListItemOut):
    """用户列表项响应——数据字段 + 审计（平铺）。"""


class UserDetailResp(UserDetailOut):
    """用户详情响应——数据字段 + 审计 + 部门引用 + 角色。"""
