"""资源 / 权限目录 HTTP schema。"""
from app.iam.application.resource.dto import CatalogOut


class CatalogResp(CatalogOut):
    """资源/权限目录响应（模块 → 资源 → 权限 三级）。"""
