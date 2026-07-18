from pydantic import BaseModel

from app.iam.domain.shared.value_objects import DeptId, UserId
from app.iam.domain.user.enums import UserType


class CurrentUser(BaseModel):
    user_id: UserId
    username: str
    nickname: str
    user_type: UserType
    roles: list | None = None
    dept_id: DeptId | None = None
    permissions: list[str] | None = None
