"""部门 CRUD + 树路由。

鉴权：功能权限由应用服务（@requires_permission）判定；接口层只 `Depends(get_current_user)` 提取身份。
路由顺序：`/tree` 必须声明在 `/{dept_id}` 之前，否则会被当成 uuid 解析。
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.application.dto import RequestMeta
from app.core.interface.http.dependencies import get_request_meta
from app.iam.application.dept.dto import UpdateDeptIn
from app.iam.application.dept.services import DeptApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import DeptId
from app.iam.interface.dependences import get_dept_app_service
from app.iam.interface.http.dependencies import get_current_user
from app.iam.interface.http.dept.schemas import (
    CreateDeptReq,
    DeptDetailResp,
    DeptListItemResp,
    DeptResp,
    DeptTreeNodeResp,
    GetDeptsReq,
    UpdateDeptReq,
)
from app.iam.interface.http.schemas import UpdateStatusReq

dept_router = APIRouter(prefix='/depts', tags=['部门'])


@dept_router.post('', response_model=DeptResp, status_code=status.HTTP_201_CREATED, summary='创建部门')
async def create_dept(
    body: CreateDeptReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> DeptResp:
    dept = await dept_app_service.create_dept(body, current_user, request_meta)
    return DeptResp.model_validate(dept, from_attributes=True)


@dept_router.get('', response_model=list[DeptListItemResp], summary='部门列表（扁平，含审计）')
async def list_depts(
    filters: Annotated[GetDeptsReq, Query()],
    current_user: CurrentUser = Depends(get_current_user),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> list[DeptListItemResp]:
    depts = await dept_app_service.get_depts(filters, current_user)
    return [DeptListItemResp(**d.model_dump()) for d in depts]


@dept_router.get('/tree', response_model=list[DeptTreeNodeResp], summary='部门树')
async def get_dept_tree(
    current_user: CurrentUser = Depends(get_current_user),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> list[DeptTreeNodeResp]:
    nodes = await dept_app_service.get_dept_tree(current_user)
    return [DeptTreeNodeResp(**n.model_dump()) for n in nodes]


@dept_router.get('/{dept_id}', response_model=DeptResp, summary='部门详情')
async def get_dept(
    dept_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> DeptResp:
    dept = await dept_app_service.get_dept(DeptId(dept_id), current_user)
    return DeptResp.model_validate(dept, from_attributes=True)


@dept_router.get('/{dept_id}/detail', response_model=DeptDetailResp, summary='部门详情（含审计）')
async def get_dept_detail(
    dept_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> DeptDetailResp:
    detail = await dept_app_service.get_dept_detail(DeptId(dept_id), current_user)
    return DeptDetailResp.model_validate(detail, from_attributes=True)


@dept_router.put('/{dept_id}', response_model=DeptResp, summary='更新部门')
async def update_dept(
    dept_id: UUID,
    body: UpdateDeptReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> DeptResp:
    data = UpdateDeptIn(id=DeptId(dept_id), **body.model_dump(exclude_unset=True))
    dept = await dept_app_service.update_dept(data, current_user, request_meta)
    return DeptResp.model_validate(dept, from_attributes=True)


@dept_router.put('/{dept_id}/status', status_code=status.HTTP_204_NO_CONTENT,
                 summary='启用/停用部门（停用级联子树，启用级联祖先）')
async def set_dept_status(
    dept_id: UUID,
    body: UpdateStatusReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> None:
    await dept_app_service.set_dept_status(
        DeptId(dept_id), body.status, current_user, request_meta)


@dept_router.delete('/{dept_id}', status_code=status.HTTP_204_NO_CONTENT,
                    summary='删除部门（软删，级联整棵子树）')
async def delete_dept(
    dept_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> None:
    await dept_app_service.delete_dept(DeptId(dept_id), current_user, request_meta)


@dept_router.post('/{dept_id}/restore', status_code=status.HTTP_204_NO_CONTENT,
                  summary='恢复部门（父已删须先恢复父；祖先非全启用时恢复为停用）')
async def restore_dept(
    dept_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> None:
    await dept_app_service.restore_dept(DeptId(dept_id), current_user, request_meta)


@dept_router.delete('/{dept_id}/hard-delete', status_code=status.HTTP_204_NO_CONTENT,
                    summary='彻底删除部门（物理，仅限已删；级联整棵子树）')
async def hard_delete_dept(
    dept_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    dept_app_service: DeptApplicationService = Depends(get_dept_app_service),
) -> None:
    await dept_app_service.hard_delete_dept(DeptId(dept_id), current_user, request_meta)
