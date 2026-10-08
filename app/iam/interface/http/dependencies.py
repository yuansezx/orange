"""HTTP 边界依赖：从请求**提取身份**。

只做适配——把令牌解成 `CurrentUser`，失败抛业务异常（→ 401）。
**权限判定不在此处**（授权是业务规则，收敛到应用服务）。
"""
from fastapi import Depends, Header

from app.iam.application.common.exceptions import InvalidTokenException
from app.iam.application.current_user.services import CurrentUserApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.interface.dependences import get_current_user_app_service


async def get_current_user(
    authorization: str | None = Header(default=None),
    current_user_app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> CurrentUser:
    """取 `Authorization: Bearer <token>`，解析为当前用户；缺/坏令牌 → InvalidTokenException（401）。"""
    if not authorization or not authorization.lower().startswith('bearer '):
        raise InvalidTokenException('未提供有效凭证')
    token = authorization[len('bearer '):].strip()
    return await current_user_app_service.get_current_user(token)
