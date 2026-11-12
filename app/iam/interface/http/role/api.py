"""角色 CRUD + 角色↔权限 / 角色↔部门 路由。

鉴权：功能权限由应用服务（@requires_permission）判定；接口层只 `Depends(get_current_user)` 提取身份。
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.application.dto import RequestMeta
from app.core.interface.http.dependencies import get_request_meta
from app.core.utils.schemas import PageResult
from app.iam.application.role.dto import UpdateRoleIn
from app.iam.application.role.services import RoleApplicationService
from app.iam.application.user_role_assignment.services import UserRoleApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import RoleId
from app.iam.interface.dependences import get_role_app_service, get_user_role_app_service
from app.iam.interface.http.dependencies import get_current_user
from app.iam.interface.http.role.schemas import (
    CreateRoleReq,
    GetRoleCandidatesReq,
    GetRoleMembersReq,
    GetRolesReq,
    PatchRoleUsersReq,
    RoleCandidateUserResp,
    RoleDetailResp,
    RoleListItemResp,
    RoleMemberResp,
    RoleResp,
    UpdateRoleReq,
)
from app.iam.interface.http.schemas import UpdateStatusReq

role_router = APIRouter(prefix='/roles', tags=['角色'])


@role_router.post('', response_model=RoleResp, status_code=status.HTTP_201_CREATED, summary='创建角色')
async def create_role(
    body: CreateRoleReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> RoleResp:
    role = await role_app_service.create_role(body, current_user, request_meta)
    return RoleResp(
        id=role.id, code=role.code, name=role.name, data_scope=role.data_scope,
        status=role.status, description=role.description,
        permission_ids=list(role.permission_ids), dept_ids=list(role.custom_dept_ids),
        created_at=role.created_at, updated_at=role.updated_at, deleted_at=role.deleted_at,
    )


@role_router.get('', response_model=PageResult[RoleListItemResp], summary='角色列表（含审计，分页）')
async def list_roles(
    filters: Annotated[GetRolesReq, Query()],
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> PageResult[RoleListItemResp]:
    page = await role_app_service.get_roles(filters, current_user)
    return PageResult[RoleListItemResp](
        page=page.page,
        page_size=page.page_size,
        total=page.total,
        data=[RoleListItemResp(**item.model_dump()) for item in (page.data or [])],
    )


@role_router.get('/{role_id}', response_model=RoleResp, summary='角色详情')
async def get_role(
    role_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> RoleResp:
    detail = await role_app_service.get_role(RoleId(role_id), current_user)
    return RoleResp.model_validate(detail, from_attributes=True)


@role_router.get('/{role_id}/detail', response_model=RoleDetailResp, summary='角色详情（含审计）')
async def get_role_detail(
    role_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> RoleDetailResp:
    detail = await role_app_service.get_role_detail(RoleId(role_id), current_user)
    return RoleDetailResp.model_validate(detail, from_attributes=True)


@role_router.get('/{role_id}/users', response_model=PageResult[RoleMemberResp],
                 summary='角色成员（分页只读）')
async def get_role_members(
    role_id: UUID,
    filters: Annotated[GetRoleMembersReq, Query()],
    current_user: CurrentUser = Depends(get_current_user),
    user_role_app_service: UserRoleApplicationService = Depends(get_user_role_app_service),
) -> PageResult[RoleMemberResp]:
    page = await user_role_app_service.get_role_members(
        RoleId(role_id), filters, current_user)
    return PageResult[RoleMemberResp](
        page=page.page,
        page_size=page.page_size,
        total=page.total,
        data=[RoleMemberResp(**item.model_dump()) for item in (page.data or [])],
    )


@role_router.get('/{role_id}/candidates', response_model=PageResult[RoleCandidateUserResp],
                 summary='角色成员候选（分页 + selected 标记）')
async def get_role_candidates(
    role_id: UUID,
    filters: Annotated[GetRoleCandidatesReq, Query()],
    current_user: CurrentUser = Depends(get_current_user),
    user_role_app_service: UserRoleApplicationService = Depends(get_user_role_app_service),
) -> PageResult[RoleCandidateUserResp]:
    page = await user_role_app_service.get_role_candidates(
        RoleId(role_id), filters, current_user)
    return PageResult[RoleCandidateUserResp](
        page=page.page,
        page_size=page.page_size,
        total=page.total,
        data=[RoleCandidateUserResp(**item.model_dump()) for item in (page.data or [])],
    )


@role_router.patch('/{role_id}/users', status_code=status.HTTP_204_NO_CONTENT,
                   summary='管理角色成员（增量）')
async def patch_role_users(
    role_id: UUID,
    body: PatchRoleUsersReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    user_role_app_service: UserRoleApplicationService = Depends(get_user_role_app_service),
) -> None:
    await user_role_app_service.patch_role_users(
        RoleId(role_id), body.add_user_ids, body.remove_user_ids, current_user, request_meta)


@role_router.put('/{role_id}', status_code=status.HTTP_204_NO_CONTENT, summary='更新角色')
async def update_role(
    role_id: UUID,
    body: UpdateRoleReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> None:
    data = UpdateRoleIn(id=RoleId(role_id), **body.model_dump())
    await role_app_service.update_role(data, current_user, request_meta)


@role_router.put('/{role_id}/status', status_code=status.HTTP_204_NO_CONTENT,
                 summary='启用/停用角色')
async def set_role_status(
    role_id: UUID,
    body: UpdateStatusReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> None:
    await role_app_service.set_role_status(
        RoleId(role_id), body.status, current_user, request_meta)


@role_router.delete('/{role_id}', status_code=status.HTTP_204_NO_CONTENT, summary='删除角色（软删）')
async def delete_role(
    role_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> None:
    await role_app_service.delete_role(RoleId(role_id), current_user, request_meta)


@role_router.post('/{role_id}/restore', status_code=status.HTTP_204_NO_CONTENT, summary='恢复角色')
async def restore_role(
    role_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> None:
    await role_app_service.restore_role(RoleId(role_id), current_user, request_meta)


@role_router.delete('/{role_id}/hard-delete', status_code=status.HTTP_204_NO_CONTENT,
                    summary='彻底删除角色（物理，仅限已删）')
async def hard_delete_role(
    role_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> None:
    await role_app_service.hard_delete_role(RoleId(role_id), current_user, request_meta)
