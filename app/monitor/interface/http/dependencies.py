"""monitor HTTP 边界的身份提取。"""
from fastapi import Depends, Request

from app.monitor.application.common.dto import CurrentUser
from app.monitor.application.common.exceptions import MonitorUnauthenticatedException
from app.monitor.application.common.ports import AuthenticationPort
from app.monitor.interface.dependences import get_authentication


def _bearer_token(request: Request) -> str:
    scheme, _, token = request.headers.get('authorization', '').partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise MonitorUnauthenticatedException('缺少或无效的 Authorization 头')
    return token


async def get_current_user(
    request: Request,
    authentication: AuthenticationPort = Depends(get_authentication),
) -> CurrentUser:
    return await authentication.authenticate(_bearer_token(request))
