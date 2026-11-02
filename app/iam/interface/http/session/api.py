"""在线会话查询与踢下线。"""
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.application.dto import RequestMeta
from app.core.interface.http.dependencies import get_request_meta
from app.iam.application.current_user.services import CurrentUserApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import UserId
from app.iam.interface.dependences import get_current_user_app_service
from app.iam.interface.http.dependencies import get_current_user
from app.iam.interface.http.session.schemas import (
    RevokeSessionsReq,
    RevokeUsersReq,
    SessionResp,
)

session_router = APIRouter(prefix='/sessions', tags=['在线会话'])


@session_router.get('', response_model=list[SessionResp], summary='在线会话列表')
async def list_sessions(
    current_user: CurrentUser = Depends(get_current_user),
    app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> list[SessionResp]:
    sessions = await app_service.list_sessions(current_user)
    return [SessionResp(**s.model_dump()) for s in sessions]


@session_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT,
                       summary='踢下线（指定会话）')
async def revoke_sessions(
    user_id: UUID,
    body: RevokeSessionsReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> None:
    await app_service.revoke_sessions(
        UserId(user_id), body.session_ids, current_user, request_meta)


@session_router.delete('', status_code=status.HTTP_204_NO_CONTENT,
                       summary='踢下线（多个用户的全部会话）')
async def revoke_users(
    body: RevokeUsersReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> None:
    await app_service.revoke_users(
        [UserId(uid) for uid in body.user_ids], current_user, request_meta)
