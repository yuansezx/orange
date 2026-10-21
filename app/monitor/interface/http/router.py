"""monitor 的 HTTP 路由汇总——对外唯一挂载单元。"""
from fastapi import APIRouter

from app.monitor.interface.http.health.api import health_router

router = APIRouter()
router.include_router(health_router)
