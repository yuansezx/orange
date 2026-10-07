from pydantic import BaseModel

from app.iam.domain.shared.value_objects import DeptId, RoleSummary, UserId
from app.iam.domain.user.enums import UserTypeEnum


class CurrentUser(BaseModel):
    user_id: UserId
    username: str
    nickname: str
    user_type: UserTypeEnum
    roles: list[RoleSummary] | None = None
    dept_id: DeptId | None = None
    permission_codes: list[str] | None = None
