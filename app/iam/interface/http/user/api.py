"""用户 CRUD 路由（create / list / update；delete 待接）。

鉴权：功能权限由应用服务（@requires_permission）判定，数据权限由服务内 access service 判定；
接口层只 `Depends(get_current_user)` 提取身份。
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.utils.schemas import PageResult
from app.iam.application.user.dto import GetUsersIn, UpdateUserIn
from app.iam.application.user.services import UserApplicationService
from app.iam.application.user_role_assignment.services import UserRoleApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import UserId
from app.iam.interface.dependences import get_user_app_service, get_user_role_app_service
from app.iam.interface.http.dependencies import get_current_user
from app.iam.interface.http.user.schemas import CreateUserReq, UpdateUserReq, UserResp

user_router = APIRouter(prefix='/users', tags=['用户'])


@user_router.post('', response_model=UserResp, status_code=status.HTTP_201_CREATED, summary='创建用户')
async def create_user(
    body: CreateUserReq,
    current_user: CurrentUser = Depends(get_current_user),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
    user_role_app_service: UserRoleApplicationService = Depends(get_user_role_app_service),
) -> UserResp:
    user = await user_app_service.create_user_by_admin(body, current_user, user_role_app_service)
    return UserResp.model_validate(user, from_attributes=True)


@user_router.get('', response_model=PageResult[UserResp], summary='用户列表')
async def list_users(
    filters: Annotated[GetUsersIn, Query()],
    current_user: CurrentUser = Depends(get_current_user),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
) -> PageResult[UserResp]:
    page = await user_app_service.get_users(filters, current_user)
    return PageResult[UserResp](
        page=page.page,
        page_size=page.page_size,
        total=page.total,
        data=[UserResp.model_validate(u, from_attributes=True) for u in (page.data or [])],
    )


@user_router.put('/{user_id}', response_model=UserResp, summary='更新用户')
async def update_user(
    user_id: UUID,
    body: UpdateUserReq,
    current_user: CurrentUser = Depends(get_current_user),
    user_app_service: UserApplicationService = Depends(get_user_app_service),
    user_role_app_service: UserRoleApplicationService = Depends(get_user_role_app_service),
) -> UserResp:
    data = UpdateUserIn(id=UserId(user_id), **body.model_dump())
    user = await user_app_service.update_user(data, current_user, user_role_app_service)
    return UserResp.model_validate(user, from_attributes=True)
