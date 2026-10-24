"""在线会话 HTTP schema。"""
from uuid import UUID

from pydantic import BaseModel, Field

from app.iam.application.current_user.dto import SessionOut


class SessionResp(SessionOut):
    """在线会话响应。"""


class RevokeSessionsReq(BaseModel):
    session_ids: list[str] = Field(min_length=1)


class RevokeUsersReq(BaseModel):
    user_ids: list[UUID] = Field(min_length=1)
