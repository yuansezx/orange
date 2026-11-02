from datetime import datetime

from pydantic import BaseModel, Field

from app.iam.application.common.dto import OperatorOut
from app.iam.domain.resource.enums import SourceTypeEnum
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId


class RegisterPermissionIn(BaseModel):
    action: str
    name: str
    description: str | None = None


class RegisterResourceIn(BaseModel):
    module: str
    code: str
    name: str
    description: str | None = None
    permissions: list[RegisterPermissionIn] = Field(default_factory=list)


class CreateResourceIn(BaseModel):
    module: str = Field(min_length=1, max_length=64)
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None


class CreatePermissionIn(BaseModel):
    resource_id: ResourceId
    action: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None


class UpdateResourceIn(BaseModel):
    """后台可改的只有展示字段；module/code 是身份，不可改。"""
    id: ResourceId
    name: str
    description: str | None = None


class UpdatePermissionIn(BaseModel):
    """后台可改的只有展示字段；action 是身份，不可改。"""
    id: PermissionId
    name: str
    description: str | None = None


class CatalogPermissionOut(BaseModel):
    id: PermissionId
    action: str
    key: str  # module:resource:action
    name: str
    description: str | None = None
    status: StatusEnum


class CatalogResourceOut(BaseModel):
    id: ResourceId
    module: str
    code: str
    key: str  # module:resource
    name: str
    description: str | None = None
    status: StatusEnum
    permissions: list[CatalogPermissionOut] = Field(default_factory=list)


class CatalogModuleOut(BaseModel):
    module: str
    resources: list[CatalogResourceOut] = Field(default_factory=list)


class CatalogOut(BaseModel):
    modules: list[CatalogModuleOut] = Field(default_factory=list)


class PermissionOut(BaseModel):
    """权限读模型（数据 + 审计，平铺）。"""
    id: PermissionId
    resource_id: ResourceId
    action: str
    key: str
    name: str
    description: str | None = None
    status: StatusEnum
    permission_type: SourceTypeEnum
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    created_by: OperatorOut | None = None
    updated_by: OperatorOut | None = None
    deleted_by: OperatorOut | None = None


class PermissionListItemOut(PermissionOut):
    """扁平权限列表项：在权限读模型上补所属资源上下文（权限回收站用）。"""
    resource_key: str
    resource_name: str


class ResourceOut(BaseModel):
    """资源读模型（数据 + 审计 + 聚合内权限）。"""
    id: ResourceId
    module: str
    code: str
    key: str
    name: str
    description: str | None = None
    status: StatusEnum
    resource_type: SourceTypeEnum
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    created_by: OperatorOut | None = None
    updated_by: OperatorOut | None = None
    deleted_by: OperatorOut | None = None
    permissions: list[PermissionOut] = Field(default_factory=list)
