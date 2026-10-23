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
from app.iam.application.user.dto import UpdateUserIn
from app.iam.application.user.services import UserApplicationService
from app.iam.application.user_role_assignment.services import UserRoleApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import UserId
from app.iam.interface.dependences import get_user_app_service, get_user_role_app_service
from app.iam.interface.http.dependencies import get_current_user
from app.iam.interface.http.schemas import UpdateStatusReq
from app.iam.interface.http.user.schemas import (
    CreateUserReq,
    GetUsersReq,
    UpdateUserReq,
    UserDetailResp,
    UserListItemResp,
    UserResp,
)

user_router = APIRouter(prefix='/users', tags=['用户'])


@user_router.post('', response_model=UserResp, status_code=status.HTTP_201_CREATED, summary='创建用户')
async def create_user(
    body: CreateUserReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
    user_role_app_service: UserRoleApplicationService = Depends(get_user_role_app_service),
) -> UserResp:
    user = await user_app_service.create_user_by_admin(
        body, current_user, user_role_app_service, request_meta)
    return UserResp.model_validate(user, from_attributes=True)


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
