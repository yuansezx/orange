from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.monitor.domain.audit_log.enums import AuditResultEnum
from app.monitor.domain.shared.value_objects import OperatorId


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
