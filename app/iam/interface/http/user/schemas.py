"""用户 HTTP schema（Req / Resp）。

字段直接用 domain 值对象（Email / Phone / DeptId），经 `SingleValueObject`
统一裸值出入、OpenAPI 展示为 string（id 带 format: uuid），无需重复写 pattern。
"""
from pydantic import BaseModel, Field

from app.iam.application.current_user.dto import MySessionOut
from app.iam.application.user.dto import (
    CreateUserIn,
    GetUsersIn,
    MyProfileOut,
    UpdateMyProfileIn,
    UserDetailOut,
    UserListItemOut,
    UserOut,
)
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, Email, Phone, RoleId, RoleSummary, UserId
from app.iam.domain.user.enums import UserTypeEnum


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


class CurrentUserResp(BaseModel):
    """当前用户响应——显式声明对外字段，避免漏出内部状态（如 data_scope_spec）。"""
    user_id: UserId
    username: str
    nickname: str
    user_type: UserTypeEnum
    roles: list[RoleSummary] | None = None
    dept_id: DeptId | None = None
    permission_codes: list[str] | None = None


class CreateUserResp(UserResp):
    """创建用户响应——服务端生成密码时一次性回传明文。"""
    temporary_password: str | None = None


class UpdateMyProfileReq(UpdateMyProfileIn):
    """自助资料更新请求——只允许昵称 / 邮箱 / 手机号。"""


class MyProfileResp(MyProfileOut):
    """自助资料响应。"""


class MySessionResp(MySessionOut):
    """自助在线设备响应。"""


class RevokeMySessionsReq(BaseModel):
    """自助踢设备请求（只会作用到本人的会话）。"""
    session_ids: list[str] = Field(min_length=1)


class ChangePasswordReq(BaseModel):
    old_password: str
    new_password: str


class ResetPasswordReq(BaseModel):
    new_password: str | None = None


class ResetPasswordResp(BaseModel):
    temporary_password: str | None = None
