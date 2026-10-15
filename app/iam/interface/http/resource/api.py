"""资源 / 权限目录路由。

鉴权：功能权限由应用服务（`@requires_permission`）判定；接口层只 `Depends(get_current_user)` 提取身份。
"""
from fastapi import APIRouter, Depends

from app.iam.application.resource.services import ResourceApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.interface.dependences import get_resource_app_service
from app.iam.interface.http.dependencies import get_current_user
from app.iam.interface.http.resource.schemas import CatalogResp

resource_router = APIRouter(prefix='/resources', tags=['资源'])


@resource_router.get('/catalog', response_model=CatalogResp, summary='资源/权限目录')
async def get_catalog(
    current_user: CurrentUser = Depends(get_current_user),
    resource_app_service: ResourceApplicationService = Depends(get_resource_app_service),
) -> CatalogResp:
    catalog = await resource_app_service.get_catalog(current_user)
    return CatalogResp.model_validate(catalog, from_attributes=True)
