from datetime import datetime

from pydantic import BaseModel, Field

from app.iam.application.common.dto import AuditOut, DeptRefOut
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import Email, Phone, RoleId, DeptId, UserId
from app.iam.domain.user.enums import UserTypeEnum


class GetUsersIn(BaseModel):
    page_size: int
    page: int
    keyword: str | None = None                          # 跨 用户名/昵称/邮箱/手机号 模糊
    user_type: UserTypeEnum | None = None
    status: StatusEnum | None = None                    # 业务状态（ACTIVE/DISABLED）
    deleted: bool = False                               # True = 只看回收站
    dept_id: DeptId | None = None
    need_change_password: bool | None = None
    created_at_start: datetime | None = None            # 时间：start/end 各自可选
    created_at_end: datetime | None = None
    password_updated_at_start: datetime | None = None
    password_updated_at_end: datetime | None = None

class CreateUserIn(BaseModel):
    username: str
    nickname: str | None = None
    password: str | None = None  # 不填则由服务端生成临时密码
    email: Email | None = None
    phone: Phone | None = None
    status: StatusEnum
    description: str | None = None
    role_ids: list[RoleId] | None = None
    dept_id: DeptId | None = None

class UpdateUserIn(BaseModel):
    id: UserId
    nickname: str
    email: Email | None = None
    phone: Phone | None = None
    status: StatusEnum
    description: str | None = None
    role_ids: list[RoleId] | None = None
    dept_id: DeptId | None = None


class UserOut(BaseModel):
    """用户数据字段（**不含 password_hash**）。"""
    id: UserId
    username: str
    nickname: str
    email: Email | None = None
    phone: Phone | None = None
    user_type: UserTypeEnum
    status: StatusEnum
    description: str | None = None
    dept_id: DeptId | None = None
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class UserListItemOut(UserOut, AuditOut):
    """用户列表项——数据字段 + 审计（平铺）。"""


class RoleRefOut(BaseModel):
    """用户详情里的角色引用（id + 标识 + 名称）。"""
    id: RoleId
    code: str
    name: str


class UserDetailOut(UserOut, AuditOut):
    """用户详情——数据字段 + 审计（平铺）+ 部门引用 + 已分配角色。"""
    dept_ref: DeptRefOut | None = None
    roles: list[RoleRefOut] = Field(default_factory=list)


class UpdateMyProfileIn(BaseModel):
    """自助资料更新：只允许昵称 / 邮箱 / 手机号。"""
    nickname: str
    email: Email | None = None
    phone: Phone | None = None


class MyProfileOut(BaseModel):
    """自助资料——本人数据 + 角色/部门，**不含**审计操作人与数据范围。"""
    user_id: UserId
    username: str
    nickname: str
    email: Email | None = None
    phone: Phone | None = None
    user_type: UserTypeEnum
    status: StatusEnum
    description: str | None = None
    dept: DeptRefOut | None = None
    roles: list[RoleRefOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None
    password_updated_at: datetime | None = None
    need_change_password: bool