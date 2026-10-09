"""HTTP 边界依赖：从请求**提取身份**。

只做适配——把令牌解成 `CurrentUser`，失败抛业务异常（→ 401）。
**权限判定不在此处**（授权是业务规则，收敛到应用服务）。
"""
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.iam.application.common.exceptions import InvalidTokenException
from app.iam.application.current_user.services import CurrentUserApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.interface.dependences import get_current_user_app_service

# auto_error=False → 缺头 / 非 Bearer 一律返回 None，由我们抛业务异常（401 + 统一错误体），
# 而非 FastAPI 默认的 403；同时产出 OpenAPI security scheme（Swagger 显示锁 + 全局 Authorize）。
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    """取 `Authorization: Bearer <token>` 的原始令牌；缺/格式不对 → InvalidTokenException（401）。"""
    if credentials is None:
        raise InvalidTokenException('未提供有效凭证')
    return credentials.credentials


async def get_current_user(
    token: str = Depends(get_bearer_token),
    current_user_app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> CurrentUser:
    """把令牌解成当前用户；令牌无效/失效 → InvalidTokenException（401）。"""
    return await current_user_app_service.get_current_user(token)
