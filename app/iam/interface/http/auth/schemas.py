from pydantic import BaseModel

from app.iam.application.current_user.dto import LoginIn, LoginOut
from app.iam.domain.shared.value_objects import DeptId, RoleSummary, UserId
from app.iam.domain.user.enums import UserTypeEnum


class LoginReq(LoginIn):
    """登录请求。线格式同 DTO，独立类型以便将来解耦。"""


class LoginResp(LoginOut):
    """登录响应。"""


class CurrentUserResp(BaseModel):
    """当前用户响应——显式声明对外字段，避免漏出内部状态（如 data_scope_spec）。"""
    user_id: UserId
    username: str
    nickname: str
    user_type: UserTypeEnum
    roles: list[RoleSummary] | None = None
    dept_id: DeptId | None = None
    permission_codes: list[str] | None = None
