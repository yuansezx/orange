"""资源 / 权限目录路由。

鉴权：功能权限由应用服务（`@requires_permission`）判定；接口层只 `Depends(get_current_user)` 提取身份。
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.application.dto import RequestMeta
from app.core.interface.http.dependencies import get_request_meta
from app.iam.application.resource.dto import UpdatePermissionIn, UpdateResourceIn
from app.iam.application.resource.services import ResourceApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId
from app.iam.interface.dependences import get_resource_app_service
from app.iam.interface.http.dependencies import get_current_user
from app.iam.interface.http.resource.schemas import (
    CatalogResp,
    CreatePermissionReq,
    CreateResourceReq,
    PermissionListItemResp,
    PermissionResp,
    ResourceListItemResp,
    ResourceResp,
    UpdatePermissionReq,
    UpdateResourceReq,
)
from app.iam.interface.http.schemas import UpdateStatusReq

resource_router = APIRouter(prefix='/resources', tags=['资源'])
permission_router = APIRouter(prefix='/permissions', tags=['权限'])


# ---------------- 资源 ----------------
@resource_router.get('/catalog', response_model=CatalogResp, summary='资源/权限目录')
async def get_catalog(
    current_user: CurrentUser = Depends(get_current_user),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> CatalogResp:
    catalog = await resource_app_service.get_catalog(current_user)
    return CatalogResp.model_validate(catalog, from_attributes=True)


@resource_router.get('', response_model=list[ResourceListItemResp],
                     summary='资源列表（含权限 + 审计）')
async def list_resources(
    status: StatusEnum | None = Query(None, description='按业务状态过滤（ACTIVE/DISABLED）'),
    deleted: bool = Query(False, description='只看回收站（缺省只看未删）'),
    include_deleted_permissions: bool = Query(
        False, description='一并返回已删权限（管理页「显示已删」用）'),
    current_user: CurrentUser = Depends(get_current_user),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> list[ResourceListItemResp]:
    resources = await resource_app_service.get_resources(
        current_user, status, deleted, include_deleted_permissions)
    return [ResourceListItemResp(**r.model_dump()) for r in resources]


@resource_router.post('', response_model=ResourceResp, status_code=status.HTTP_201_CREATED,
                      summary='新建自定义资源')
async def create_resource(
    body: CreateResourceReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> ResourceResp:
    resource = await resource_app_service.create_resource(body, current_user, request_meta)
    return ResourceResp(**resource.model_dump())


@resource_router.put('/{resource_id}', status_code=status.HTTP_204_NO_CONTENT,
                     summary='更新资源')
async def update_resource(
    resource_id: UUID,
    body: UpdateResourceReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    data = UpdateResourceIn(id=ResourceId(resource_id), **body.model_dump())
    await resource_app_service.update_resource(data, current_user, request_meta)


@resource_router.put('/{resource_id}/status', status_code=status.HTTP_204_NO_CONTENT,
                     summary='启用/停用资源')
async def set_resource_status(
    resource_id: UUID,
    body: UpdateStatusReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    await resource_app_service.set_resource_status(
        ResourceId(resource_id), body.status, current_user, request_meta)


@resource_router.delete('/{resource_id}', status_code=status.HTTP_204_NO_CONTENT,
                        summary='删除资源（软删，级联权限）')
async def delete_resource(
    resource_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    await resource_app_service.delete_resource(ResourceId(resource_id), current_user, request_meta)


@resource_router.post('/{resource_id}/restore', status_code=status.HTTP_204_NO_CONTENT,
                      summary='恢复资源（含其权限）')
async def restore_resource(
    resource_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    await resource_app_service.restore_resource(ResourceId(resource_id), current_user, request_meta)


@resource_router.delete('/{resource_id}/hard-delete', status_code=status.HTTP_204_NO_CONTENT,
                        summary='彻底删除资源（物理，仅限已删）')
async def hard_delete_resource(
    resource_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    await resource_app_service.hard_delete_resource(
        ResourceId(resource_id), current_user, request_meta)


# ---------------- 权限（聚合内实体） ----------------
@permission_router.get('', response_model=list[PermissionListItemResp],
                       summary='权限扁平列表（含所属资源 + 审计）')
async def list_permissions(
    deleted: bool = Query(False, description='权限回收站：只列资源仍存活的已删权限'),
    current_user: CurrentUser = Depends(get_current_user),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> list[PermissionListItemResp]:
    permissions = await resource_app_service.get_permissions(current_user, deleted)
    return [PermissionListItemResp(**p.model_dump()) for p in permissions]


@permission_router.post('', response_model=PermissionResp, status_code=status.HTTP_201_CREATED,
                        summary='新建自定义权限')
async def create_permission(
    body: CreatePermissionReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> PermissionResp:
    permission = await resource_app_service.create_permission(body, current_user, request_meta)
    return PermissionResp(**permission.model_dump())


@permission_router.put('/{permission_id}', status_code=status.HTTP_204_NO_CONTENT,
                       summary='更新权限')
async def update_permission(
    permission_id: UUID,
    body: UpdatePermissionReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    data = UpdatePermissionIn(id=PermissionId(permission_id), **body.model_dump())
    await resource_app_service.update_permission(data, current_user, request_meta)


@permission_router.put('/{permission_id}/status', status_code=status.HTTP_204_NO_CONTENT,
                       summary='启用/停用权限')
async def set_permission_status(
    permission_id: UUID,
    body: UpdateStatusReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    await resource_app_service.set_permission_status(
        PermissionId(permission_id), body.status, current_user, request_meta)


@permission_router.delete('/{permission_id}', status_code=status.HTTP_204_NO_CONTENT,
                          summary='删除权限（软删）')
async def delete_permission(
    permission_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    await resource_app_service.delete_permission(
        PermissionId(permission_id), current_user, request_meta)


@permission_router.post('/{permission_id}/restore', status_code=status.HTTP_204_NO_CONTENT,
                        summary='恢复权限')
async def restore_permission(
    permission_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    await resource_app_service.restore_permission(
        PermissionId(permission_id), current_user, request_meta)


@permission_router.delete('/{permission_id}/hard-delete',
                          status_code=status.HTTP_204_NO_CONTENT,
                          summary='彻底删除权限（物理，仅限已删）')
async def hard_delete_permission(
    permission_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> None:
    await resource_app_service.hard_delete_permission(
        PermissionId(permission_id), current_user, request_meta)
