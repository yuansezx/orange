"""iam 的 HTTP 路由汇总——对外**唯一挂载单元**。

app 工厂按 `core.modules` 动态 include 本模块；路由本体在各自的 `{resource}/api.py`。
"""
from fastapi import APIRouter

from app.iam.interface.http.auth.api import auth_router
from app.iam.interface.http.dept.api import dept_router
from app.iam.interface.http.role.api import role_router
from app.iam.interface.http.user.api import user_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(dept_router)
router.include_router(role_router)
