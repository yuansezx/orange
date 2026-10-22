from fastapi import Request
from future_uuid import uuid7

from app.core.application.dto import RequestMeta


def get_request_meta(request: Request) -> RequestMeta:
    """构造请求级技术元数据（FastAPI 同一请求内缓存，天然单例）。"""
    return RequestMeta(
        request_id=request.headers.get('x-request-id') or str(uuid7()),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get('user-agent'),
    )
