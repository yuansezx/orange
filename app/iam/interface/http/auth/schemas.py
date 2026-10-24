"""认证 HTTP schema。"""
from app.iam.application.current_user.dto import LoginIn, LoginOut


class LoginReq(LoginIn):
    """登录请求。线格式同 DTO，独立类型以便将来解耦。"""


class LoginResp(LoginOut):
    """登录响应。"""
