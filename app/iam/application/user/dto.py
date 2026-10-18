from datetime import datetime

from pydantic import BaseModel

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
    password: str
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