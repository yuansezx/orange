from pydantic import BaseModel


class RequestMeta(BaseModel):
    """请求级技术元数据（request_id / IP / UA）。

    由 HTTP 边界构造后**显式**传给写用例；不属于身份，不进 `CurrentUser` 缓存。
    """
    request_id: str
    ip: str | None = None
    user_agent: str | None = None
