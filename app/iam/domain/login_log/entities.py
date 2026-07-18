from datetime import datetime

from pydantic import BaseModel


class LoginLog(BaseModel):
    id: int
    user_id: int
    ip: str
    login_at: datetime
    is_success: bool
    fail_reason: str | None = None
