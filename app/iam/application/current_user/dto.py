from pydantic import BaseModel


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    expires_in: int  # 秒
    need_change_password: bool = False
