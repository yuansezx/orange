"""monitor 健康检查（公开端点，不鉴权）。"""
from fastapi import APIRouter

from app.core.infrastructure.settings import CORE_SETTINGS
from app.monitor.interface.http.health.schemas import HealthResp

health_router = APIRouter(prefix='/health', tags=['监控'])


@health_router.get('', response_model=HealthResp, summary='健康检查')
async def health() -> HealthResp:
    return HealthResp(
        status='ok',
        module='monitor',
        app_name=CORE_SETTINGS.app_name,
        app_version=CORE_SETTINGS.app_version,
    )
