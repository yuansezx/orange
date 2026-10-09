"""用户 HTTP schema（Req / Resp）。

字段直接用 domain 值对象（UserId / Email / Phone / DeptId），经 `SingleValueObject`
统一裸值出入、OpenAPI 展示为 string（id 带 format: uuid），无需重复写 pattern。
"""
from datetime import datetime

from pydantic import BaseModel

from app.iam.application.user.dto import CreateUserIn
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, Email, Phone, RoleId, UserId
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


class UserResp(BaseModel):
    """用户响应——显式字段（**不含 password_hash**）。"""
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
