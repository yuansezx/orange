from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.monitor.domain.audit_log.enums import AuditResultEnum
from app.monitor.domain.shared.value_objects import AuditLogId, OperatorId


class AuditLogIn(BaseModel):
    """审计写入输入（其他模块通过 monitor 的公开 Python API 传入）。

    `id` 由 monitor 在写入时生成（UUIDv7）；`occurred_at` 不传则取当前时间。
    """

    occurred_at: datetime | None = None

    module: str = Field(min_length=1, max_length=64)
    resource: str = Field(min_length=1, max_length=64)
    action: str = Field(min_length=1, max_length=64)
    summary: str = Field(min_length=1, max_length=512)

    target_type: str | None = Field(default=None, max_length=64)
    target_id: str | None = Field(default=None, max_length=128)
    target_name: str | None = Field(default=None, max_length=255)

    operator_id: OperatorId | None = None
    operator_username: str | None = Field(default=None, max_length=64)
    operator_nickname: str | None = Field(default=None, max_length=128)

    result: AuditResultEnum
    error_code: str | None = Field(default=None, max_length=128)
    error_message: str | None = Field(default=None, max_length=1024)

    request_id: str | None = Field(default=None, max_length=64)
    ip: str | None = Field(default=None, max_length=64)
    user_agent: str | None = Field(default=None, max_length=512)

    detail: dict[str, Any] = Field(default_factory=dict)


class GetAuditLogsIn(BaseModel):
    """审计日志列表查询。"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)

    module: str | None = None
    resource: str | None = None
    action: str | None = None
    operator_id: OperatorId | None = None
    operator_username: str | None = None
    target_type: str | None = None
    target_id: str | None = None
    result: AuditResultEnum | None = None
    request_id: str | None = None
    keyword: str | None = None
    occurred_from: datetime | None = None
    occurred_to: datetime | None = None


class AuditLogOut(BaseModel):
    """审计日志读模型。"""
    id: AuditLogId
    occurred_at: datetime
    module: str
    resource: str
    action: str
    key: str
    summary: str

    target_type: str | None = None
    target_id: str | None = None
    target_name: str | None = None

    operator_id: OperatorId | None = None
    operator_username: str | None = None
    operator_nickname: str | None = None

    result: AuditResultEnum
    error_code: str | None = None
    error_message: str | None = None

    request_id: str | None = None
    ip: str | None = None
    user_agent: str | None = None

    detail: dict[str, Any] = Field(default_factory=dict)
