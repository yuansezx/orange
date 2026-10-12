"""角色 CRUD + 角色↔权限 / 角色↔部门 路由。

鉴权：功能权限由应用服务（@requires_permission）判定；接口层只 `Depends(get_current_user)` 提取身份。
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.iam.application.role.dto import SetRoleDeptsIn, SetRolePermissionsIn, UpdateRoleIn
from app.iam.application.role.services import RoleApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import RoleId
from app.iam.interface.dependences import get_role_app_service
from app.iam.interface.http.dependencies import get_current_user
from app.iam.interface.http.role.schemas import (
    CreateRoleReq,
    RoleDetailResp,
    RoleResp,
    SetRoleDeptsReq,
    SetRolePermissionsReq,
    UpdateRoleReq,
)

role_router = APIRouter(prefix='/roles', tags=['角色'])


@role_router.post('', response_model=RoleDetailResp, status_code=status.HTTP_201_CREATED, summary='创建角色')
async def create_role(
    body: CreateRoleReq,
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> RoleDetailResp:
    role = await role_app_service.create_role(body, current_user)
    return RoleDetailResp(
        id=role.id, code=role.code, name=role.name, data_scope=role.data_scope,
        status=role.status, description=role.description,
        permission_ids=list(role.permission_ids), dept_ids=list(role.custom_dept_ids),
    )


@role_router.get('', response_model=list[RoleResp], summary='角色列表')
async def list_roles(
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> list[RoleResp]:
    roles = await role_app_service.get_all_roles(current_user)
    return [RoleResp.model_validate(r, from_attributes=True) for r in roles]


@role_router.get('/{role_id}', response_model=RoleDetailResp, summary='角色详情')
async def get_role(
    role_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> RoleDetailResp:
    detail = await role_app_service.get_role(RoleId(role_id), current_user)
    return RoleDetailResp.model_validate(detail, from_attributes=True)


@role_router.put('/{role_id}', status_code=status.HTTP_204_NO_CONTENT, summary='更新角色')
async def update_role(
    role_id: UUID,
    body: UpdateRoleReq,
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> None:
    data = UpdateRoleIn(id=RoleId(role_id), **body.model_dump(exclude_unset=True))
    await role_app_service.update_role(data, current_user)


@role_router.put('/{role_id}/permissions', status_code=status.HTTP_204_NO_CONTENT, summary='设置角色权限')
async def set_role_permissions(
    role_id: UUID,
    body: SetRolePermissionsReq,
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> None:
    await role_app_service.set_role_permissions(
        SetRolePermissionsIn(role_id=RoleId(role_id), permission_ids=body.permission_ids), current_user)


@role_router.put('/{role_id}/depts', status_code=status.HTTP_204_NO_CONTENT, summary='设置角色数据范围部门')
async def set_role_depts(
    role_id: UUID,
    body: SetRoleDeptsReq,
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> None:
    await role_app_service.set_role_depts(
        SetRoleDeptsIn(role_id=RoleId(role_id), dept_ids=body.dept_ids), current_user)


@role_router.delete('/{role_id}', status_code=status.HTTP_204_NO_CONTENT, summary='删除角色')
async def delete_role(
    role_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    role_app_service: RoleApplicationService = Depends(get_role_app_service),
) -> None:
    await role_app_service.delete_role(RoleId(role_id), current_user)
