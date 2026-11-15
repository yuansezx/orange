"""系统信息路由（平台/模块版本）。"""
from fastapi import APIRouter, Depends

from app.monitor.application.common.dto import CurrentUser
from app.monitor.application.system.services import SystemInfoApplicationService
from app.monitor.interface.dependences import get_system_info_app_service
from app.monitor.interface.http.dependencies import get_current_user
from app.monitor.interface.http.system.schemas import ModuleVersionResp, SystemVersionsResp

system_router = APIRouter(prefix='/system', tags=['系统信息'])


@system_router.get('/versions', response_model=SystemVersionsResp,
                   summary='平台与模块版本')
async def get_versions(
    current_user: CurrentUser = Depends(get_current_user),
    app_service: SystemInfoApplicationService = Depends(get_system_info_app_service),
) -> SystemVersionsResp:
    result = await app_service.get_versions(current_user)
    return SystemVersionsResp(
        platform_version=result.platform_version,
        modules=[ModuleVersionResp(**item.model_dump()) for item in result.modules],
    )
