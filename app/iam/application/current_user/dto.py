from datetime import datetime

from pydantic import BaseModel

from app.iam.domain.shared.value_objects import UserId


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    expires_in: int  # 秒
    need_change_password: bool = False


class SessionOut(BaseModel):
    """在线会话视图（用户信息在列表时由快照/用户表补充）。"""
    user_id: UserId
    username: str | None = None
    nickname: str | None = None
    session_id: str
    login_at: datetime
    expires_at: datetime
    login_ip: str | None = None
    login_user_agent: str | None = None
