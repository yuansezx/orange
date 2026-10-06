from pydantic import BaseModel, Field

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
    module: str
    code: str
    name: str
    description: str | None = None


class CreatePermissionIn(BaseModel):
    resource_id: ResourceId
    action: str
    name: str
    description: str | None = None


class UpdateResourceIn(BaseModel):
    id: ResourceId
    name: str | None = None
    description: str | None = None
    status: StatusEnum | None = None


class UpdatePermissionIn(BaseModel):
    id: PermissionId
    name: str | None = None
    description: str | None = None
    status: StatusEnum | None = None


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
