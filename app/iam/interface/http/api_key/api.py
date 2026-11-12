"""API Key 自助路由 + 后台管理路由。"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.application.dto import RequestMeta
from app.core.interface.http.dependencies import get_request_meta
from app.iam.application.api_key.services import ApiKeyApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import ApiKeyId
from app.iam.interface.dependences import get_api_key_app_service
from app.iam.interface.http.api_key.schemas import (
    ApiKeyAdminResp,
    ApiKeyCreatedResp,
    ApiKeyResp,
    CreateApiKeyReq,
    GetApiKeysReq,
    ScopeCandidateResp,
    UpdateApiKeyReq,
)
from app.iam.interface.http.dependencies import get_current_user
from app.iam.interface.http.schemas import UpdateStatusReq

self_api_key_router = APIRouter(prefix='/users/me/api-keys', tags=['我的 API Key'])
admin_api_key_router = APIRouter(prefix='/api-keys', tags=['API Key 管理'])


# ---------------- 自助 ----------------

@self_api_key_router.get('', response_model=list[ApiKeyResp], summary='我的 API Key 列表')
async def list_my_api_keys(
    current_user: CurrentUser = Depends(get_current_user),
    app_service: ApiKeyApplicationService = Depends(get_api_key_app_service),
) -> list[ApiKeyResp]:
    return [ApiKeyResp(**item.model_dump()) for item in await app_service.list_my(current_user)]


@self_api_key_router.get('/scope-candidates', response_model=list[ScopeCandidateResp],
                         summary='可授予的权限候选')
async def list_scope_candidates(
    current_user: CurrentUser = Depends(get_current_user),
    app_service: ApiKeyApplicationService = Depends(get_api_key_app_service),
) -> list[ScopeCandidateResp]:
    return [ScopeCandidateResp(**item.model_dump())
            for item in await app_service.scope_candidates(current_user)]


@self_api_key_router.post('', response_model=ApiKeyCreatedResp,
                          status_code=status.HTTP_201_CREATED, summary='创建 API Key')
async def create_api_key(
    body: CreateApiKeyReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    app_service: ApiKeyApplicationService = Depends(get_api_key_app_service),
) -> ApiKeyCreatedResp:
    created = await app_service.create(body, current_user, request_meta)
    return ApiKeyCreatedResp(**created.model_dump())


@self_api_key_router.put('/{api_key_id}', response_model=ApiKeyResp, summary='更新 API Key')
async def update_api_key(
    api_key_id: UUID,
    body: UpdateApiKeyReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    app_service: ApiKeyApplicationService = Depends(get_api_key_app_service),
) -> ApiKeyResp:
    updated = await app_service.update(ApiKeyId(api_key_id), body, current_user, request_meta)
    return ApiKeyResp(**updated.model_dump())


@self_api_key_router.put('/{api_key_id}/status', response_model=ApiKeyResp,
                         summary='启用/停用 API Key')
async def change_api_key_status(
    api_key_id: UUID,
    body: UpdateStatusReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    app_service: ApiKeyApplicationService = Depends(get_api_key_app_service),
) -> ApiKeyResp:
    updated = await app_service.change_status(
        ApiKeyId(api_key_id), body.status, current_user, request_meta)
    return ApiKeyResp(**updated.model_dump())


@self_api_key_router.delete('/{api_key_id}', status_code=status.HTTP_204_NO_CONTENT,
                            summary='吊销 API Key')
async def revoke_api_key(
    api_key_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    app_service: ApiKeyApplicationService = Depends(get_api_key_app_service),
) -> None:
    await app_service.revoke(ApiKeyId(api_key_id), current_user, request_meta)


# ---------------- 后台管理 ----------------

@admin_api_key_router.get('', response_model=list[ApiKeyAdminResp],
                          summary='全部 API Key（后台管理）')
async def list_all_api_keys(
    filters: Annotated[GetApiKeysReq, Query()],
    current_user: CurrentUser = Depends(get_current_user),
    app_service: ApiKeyApplicationService = Depends(get_api_key_app_service),
) -> list[ApiKeyAdminResp]:
    return [ApiKeyAdminResp(**item.model_dump())
            for item in await app_service.list_all(filters, current_user)]


@admin_api_key_router.put('/{api_key_id}/status', response_model=ApiKeyAdminResp,
                          summary='启用/停用指定 API Key（后台管理）')
async def admin_change_api_key_status(
    api_key_id: UUID,
    body: UpdateStatusReq,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    app_service: ApiKeyApplicationService = Depends(get_api_key_app_service),
) -> ApiKeyAdminResp:
    updated = await app_service.admin_change_status(
        ApiKeyId(api_key_id), body.status, current_user, request_meta)
    return ApiKeyAdminResp(**updated.model_dump())


@admin_api_key_router.delete('/{api_key_id}', status_code=status.HTTP_204_NO_CONTENT,
                             summary='吊销指定 API Key（后台管理）')
async def admin_revoke_api_key(
    api_key_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    request_meta: RequestMeta = Depends(get_request_meta),
    app_service: ApiKeyApplicationService = Depends(get_api_key_app_service),
) -> None:
    await app_service.admin_revoke(ApiKeyId(api_key_id), current_user, request_meta)
