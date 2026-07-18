from datetime import datetime

from pydantic import BaseModel

from app.iam.domain.shared.enums import Status
from app.iam.domain.shared.value_objects import Email, Phone, RoleId, DeptId, UserId


class GetUsersIn(BaseModel):
    page_size: int
    page: int
    username: str | None = None
    nickname: str | None = None
    email: str | None = None
    phone: str | None = None
    status: Status | None = None
    remark: str | None = None
    dept_id: DeptId | None = None
    created_at_between: tuple[datetime, datetime] | None = None

class CreateUserIn(BaseModel):
    username: str
    nickname: str | None = None
    password: str
    email: Email | None = None
    phone: Phone | None = None
    status: Status
    remark: str | None = None
    role_ids: list[RoleId] | None = None
    dept_id: DeptId | None = None

class UpdateUserIn(BaseModel):
    id: UserId
    nickname: str
    email: Email | None = None
    phone: Phone | None = None
    status: Status
    remark: str | None = None
    role_ids: list[RoleId] | None = None
    dept_id: DeptId | None = None