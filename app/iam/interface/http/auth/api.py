"""认证三件套：login / logout / me。"""
from fastapi import APIRouter, Depends, status

from app.iam.application.current_user.services import CurrentUserApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.interface.dependences import get_current_user_app_service
from app.iam.interface.http.auth.schemas import CurrentUserResp, LoginReq, LoginResp
from app.iam.interface.http.dependencies import get_bearer_token, get_current_user

auth_router = APIRouter(prefix='/auth', tags=['认证'])


@auth_router.post('/login', response_model=LoginResp, summary='登录')
async def login(
    body: LoginReq,
    current_user_app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> LoginResp:
    out = await current_user_app_service.login(body)
    return LoginResp(**out.model_dump())


@auth_router.post('/logout', status_code=status.HTTP_204_NO_CONTENT, summary='登出（吊销当前令牌）')
async def logout(
    token: str = Depends(get_bearer_token),
    current_user_app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> None:
    await current_user_app_service.logout(token)


@auth_router.get('/me', response_model=CurrentUserResp, summary='当前用户')
async def me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUserResp:
    return CurrentUserResp.model_validate(current_user, from_attributes=True)
