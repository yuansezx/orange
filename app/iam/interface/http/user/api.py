"""用户 CRUD 路由（create / list / update / delete）+ 回收站（restore / hard-delete）。

鉴权：功能权限由应用服务（@requires_permission）判定，数据权限由服务内 access service 判定；
接口层只 `Depends(get_current_user)` 提取身份。
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.application.dto import RequestMeta
from app.core.interface.http.dependencies import get_request_meta
from app.core.utils.schemas import PageResult
from app.iam.application.current_user.dto import ChangePasswordIn
from app.iam.application.current_user.services import CurrentUserApplicationService
from app.iam.application.user.dto import UpdateUserIn
from app.iam.application.user.services import UserApplicationService
from app.iam.application.user_role_assignment.services import UserRoleApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import UserId
from app.iam.interface.dependences import (
    get_current_user_app_service,
    get_user_app_service,
    get_user_role_app_service,
)
from app.iam.interface.http.dependencies import get_current_session_id, get_current_user
from app.iam.interface.http.schemas import UpdateStatusReq
from app.iam.interface.http.user.schemas import (
    ChangePasswordReq,
    CreateUserReq,
    CreateUserResp,
    CurrentUserResp,
    GetUsersReq,
    MyProfileResp,
    MySessionResp,
    ResetPasswordReq,
    ResetPasswordResp,
    RevokeMySessionsReq,
    UpdateMyProfileReq,
    UpdateUserReq,
    UserDetailResp,
    UserListItemResp,
    UserResp,
)

user_router = APIRouter(prefix='/users', tags=['用户'])


@user_router.post('', response_model=CreateUserResp, status_code=status.HTTP_201_CREATED, summary='创建用户')
async def create_user(
    body: CreateUserReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
    user_role_app_service: UserRoleApplicationService = Depends(get_user_role_app_service),
) -> CreateUserResp:
    user, temporary_password = await user_app_service.create_user_by_admin(
        body, current_user, user_role_app_service, request_meta)
    return CreateUserResp(
        **UserResp.model_validate(user, from_attributes=True).model_dump(),
        temporary_password=temporary_password,
    )


@user_router.get('', response_model=PageResult[UserListItemResp], summary='用户列表（含审计）')
async def list_users(
    filters: Annotated[GetUsersReq, Query()],
    current_user: CurrentUser = Depends(get_current_user),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> PageResult[UserListItemResp]:
    page = await user_app_service.get_users(filters, current_user)
    return PageResult[UserListItemResp](
        page=page.page,
        page_size=page.page_size,
        total=page.total,
        data=[UserListItemResp(**item.model_dump()) for item in (page.data or [])],
    )


@user_router.get('/me', response_model=CurrentUserResp, summary='当前用户')
async def get_me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUserResp:
    return CurrentUserResp.model_validate(current_user, from_attributes=True)


@user_router.put('/me/password', status_code=status.HTTP_204_NO_CONTENT,
                 summary='修改当前用户密码')
async def change_my_password(
    body: ChangePasswordReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    current_user_app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> None:
    await current_user_app_service.change_password(
        ChangePasswordIn(**body.model_dump()), current_user, request_meta)


@user_router.get('/me/profile', response_model=MyProfileResp, summary='我的个人资料')
async def get_my_profile(
    current_user: CurrentUser = Depends(get_current_user),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> MyProfileResp:
    profile = await user_app_service.get_my_profile(current_user)
    return MyProfileResp(**profile.model_dump())


@user_router.put('/me/profile', response_model=MyProfileResp, summary='更新我的个人资料')
async def update_my_profile(
    body: UpdateMyProfileReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> MyProfileResp:
    profile = await user_app_service.update_my_profile(body, current_user, request_meta)
    return MyProfileResp(**profile.model_dump())


@user_router.get('/me/sessions', response_model=list[MySessionResp],
                 summary='我的在线设备')
async def list_my_sessions(
    current_user: CurrentUser = Depends(get_current_user),
    current_session_id: str = Depends(get_current_session_id),
    app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> list[MySessionResp]:
    sessions = await app_service.list_my_sessions(current_user, current_session_id)
    return [MySessionResp(**session.model_dump()) for session in sessions]


@user_router.delete('/me/sessions', status_code=status.HTTP_204_NO_CONTENT,
                    summary='退出登录设备')
async def revoke_my_sessions(
    body: RevokeMySessionsReq,
    current_user: CurrentUser = Depends(get_current_user),
    current_session_id: str = Depends(get_current_session_id),
    request_meta: RequestMeta = Depends(get_request_meta),
    app_service: CurrentUserApplicationService = Depends(get_current_user_app_service),
) -> None:
    await app_service.revoke_my_sessions(
        set(body.session_ids), current_user, current_session_id, request_meta)


@user_router.get('/{user_id}/detail', response_model=UserDetailResp,
                 summary='用户详情（含审计 / 部门 / 角色）')
async def get_user_detail(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> UserDetailResp:
    detail = await user_app_service.get_user_detail(UserId(user_id), current_user)
    return UserDetailResp(**detail.model_dump())


@user_router.put('/{user_id}', response_model=UserResp, summary='更新用户')
async def update_user(
    user_id: UUID,
    body: UpdateUserReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
    user_role_app_service: UserRoleApplicationService = Depends(get_user_role_app_service),
) -> UserResp:
    data = UpdateUserIn(id=UserId(user_id), **body.model_dump())
    user = await user_app_service.update_user(
        data, current_user, user_role_app_service, request_meta)
    return UserResp.model_validate(user, from_attributes=True)


@user_router.put('/{user_id}/status', status_code=status.HTTP_204_NO_CONTENT,
                 summary='启用/停用用户')
async def set_user_status(
    user_id: UUID,
    body: UpdateStatusReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> None:
    await user_app_service.set_user_status(
        UserId(user_id), body.status, current_user, request_meta)


@user_router.put('/{user_id}/password', response_model=ResetPasswordResp,
                 summary='重置用户密码')
async def reset_user_password(
    user_id: UUID,
    body: ResetPasswordReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> ResetPasswordResp:
    temporary_password = await user_app_service.reset_user_password(
        UserId(user_id), body.new_password, current_user, request_meta)
    return ResetPasswordResp(temporary_password=temporary_password)


@user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT, summary='删除用户（软删）')
async def delete_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> None:
    await user_app_service.delete_user(UserId(user_id), current_user, request_meta)


@user_router.post('/{user_id}/restore', status_code=status.HTTP_204_NO_CONTENT, summary='恢复用户')
async def restore_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> None:
    await user_app_service.restore_user(UserId(user_id), current_user, request_meta)


@user_router.delete('/{user_id}/hard-delete', status_code=status.HTTP_204_NO_CONTENT,
                    summary='彻底删除用户（物理，仅限已删）')
async def hard_delete_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> None:
    await user_app_service.hard_delete_user(UserId(user_id), current_user, request_meta)
