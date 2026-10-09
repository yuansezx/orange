from app.iam.application.current_user.dto import LoginIn, LoginOut
from app.iam.domain.current_user.entities import CurrentUser


class LoginReq(LoginIn):
    """登录请求。线格式同 DTO，独立类型以便将来解耦。"""


class LoginResp(LoginOut):
    """登录响应。"""


class CurrentUserResp(CurrentUser):
    """当前用户响应。线格式同领域实体（单值 VO 已裸值化，结构化 VO 保持对象）。"""
