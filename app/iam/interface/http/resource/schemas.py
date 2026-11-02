"""资源 / 权限 HTTP schema（Req / Resp）。"""
from pydantic import BaseModel

from app.iam.application.resource.dto import (
    CatalogOut,
    CreatePermissionIn,
    CreateResourceIn,
    PermissionListItemOut,
    PermissionOut,
    ResourceOut,
)


class CreateResourceReq(CreateResourceIn):
    """新建自定义资源请求——线格式同 DTO。"""


class UpdateResourceReq(BaseModel):
    """更新资源请求——module/code 是身份、不可改；状态走独立接口。"""
    name: str
    description: str | None = None


class CreatePermissionReq(CreatePermissionIn):
    """新建自定义权限请求——线格式同 DTO。"""


class UpdatePermissionReq(BaseModel):
    """更新权限请求——action 是身份、不可改；状态走独立接口。"""
    name: str
    description: str | None = None


class ResourceResp(ResourceOut):
    """资源响应（数据 + 审计 + 聚合内权限）。"""


class ResourceListItemResp(ResourceOut):
    """资源列表项响应——与资源响应同 schema。"""


class PermissionResp(PermissionOut):
    """权限响应（数据 + 审计）。"""


class PermissionListItemResp(PermissionListItemOut):
    """扁平权限列表项响应（含所属资源 + 审计）。"""


class CatalogResp(CatalogOut):
    """资源/权限目录响应（模块 → 资源 → 权限 三级）。"""
