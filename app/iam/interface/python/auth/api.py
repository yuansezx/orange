"""iam 的认证公开 Python API。"""
from app.iam.interface.dependences import get_current_user_app_service
from app.iam.interface.python.auth.schemas import CurrentUserResp

__all__ = ['get_current_user']


async def get_current_user(token: str) -> CurrentUserResp:
    """校验令牌并返回当前用户上下文；失败抛 `IAM_INVALID_TOKEN`。"""
    current_user = await get_current_user_app_service().get_current_user(token)
    return CurrentUserResp.model_validate(current_user, from_attributes=True)
