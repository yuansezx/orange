"""认证：login / logout。"""
from fastapi import APIRouter, Depends, status

from app.core.application.dto import RequestMeta
from app.core.interface.http.dependencies import get_request_meta
from app.iam.application.current_user.services import CurrentUserApplicationService
from app.iam.interface.dependences import get_current_user_app_service
from app.iam.interface.http.auth.schemas import LoginReq, LoginResp
from app.iam.interface.http.dependencies import get_bearer_token

auth_router = APIRouter(prefix='/auth', tags=['认证'])


@auth_router.post('/login', response_model=LoginResp, summary='登录')
async def login(
    body: LoginReq,
    request_meta: RequestMeta = Depends(get_request_meta),
    current_user_app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> LoginResp:
    out = await current_user_app_service.login(body, request_meta)
    return LoginResp(**out.model_dump())


@auth_router.post('/logout', status_code=status.HTTP_204_NO_CONTENT, summary='登出（吊销当前令牌）')
async def logout(
    token: str = Depends(get_bearer_token),
    current_user_app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> None:
    await current_user_app_service.logout(token)
