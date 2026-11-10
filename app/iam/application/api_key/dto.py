"""API Key 管理用例的应用层 DTO。"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum
from app.iam.domain.shared.value_objects import ApiKeyId, DeptId, UserId


class CreateApiKeyIn(BaseModel):
    name: str
    scopes: list[str]
    data_scope_kind: DataScopeEnum = DataScopeEnum.ALL
    data_scope_dept_ids: list[DeptId] = Field(default_factory=list)
    # 省略 = 默认 90 天；显式 null = 不限期
    expires_at: datetime | None = None


class UpdateApiKeyIn(BaseModel):
    """PUT 全量替换可编辑字段；`expires_at=None` 表示不限期。"""
    name: str
    scopes: list[str]
    data_scope_kind: DataScopeEnum
    data_scope_dept_ids: list[DeptId] = Field(default_factory=list)
    expires_at: datetime | None = None


class ApiKeyOut(BaseModel):
    id: ApiKeyId
    name: str
    token_masked: str
    scopes: list[str]
    data_scope_kind: DataScopeEnum
    data_scope_dept_ids: list[DeptId]
    status: StatusEnum
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ApiKeyCreatedOut(ApiKeyOut):
    token: str  # 明文仅创建时返回一次


class ApiKeyAdminOut(ApiKeyOut):
    user_id: UserId
    username: str | None = None
    nickname: str | None = None


class GetApiKeysIn(BaseModel):
    user_id: UserId | None = None
    status: StatusEnum | None = None
    deleted: bool = False


class PermissionCandidateOut(BaseModel):
    code: str
    action: str
    name: str


class ResourceCandidateOut(BaseModel):
    module: str
    resource: str
    name: str
    permissions: list[PermissionCandidateOut]
