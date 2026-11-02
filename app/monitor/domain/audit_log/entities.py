from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.monitor.domain.audit_log.enums import AuditResultEnum
from app.monitor.domain.audit_log.exceptions import InvalidAuditLogException
from app.monitor.domain.shared.value_objects import AuditLogId, OperatorId


class AuditLog(BaseModel):
    """审计日志（**只追加**，不更新、不软删）。

    - 动作码由 `module:resource:action` 运行时派生（如 `iam:user:create`）。
    - `resource` 是被操作的**聚合根码**（user / role / dept / resource / user_role /
      current_user …），不是具体实例；`target_type/target_id` 才是具体对象。
    - 操作人与目标都存**事件发生时的快照**：后续改名/删除不影响历史可读性。
    - `summary` 是给列表展示的人类可读一句话；`error_code` / `error_message`
      只在失败时填写，成功时必须为空。
    - `detail` 放动作特有的结构化载荷（before/after、权限 id 等）；敏感字段
      由生产方在写入前脱敏。
    - `occurred_at` 是业务事件发生时间（须带时区）；持久化时间由仓储层另行记录。
    """

    model_config = ConfigDict(frozen=True)

    id: AuditLogId
    occurred_at: datetime

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

    @property
    def full_code(self) -> str:
        """完整动作码 `module:resource:action`（运行时派生，不落库）。"""
        return f'{self.module}:{self.resource}:{self.action}'

    @field_validator('occurred_at')
    @classmethod
    def _require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError('occurred_at 必须带时区')
        return value

    @model_validator(mode='after')
    def _check_code_parts(self):
        """三段码都不允许包含分隔符 ':'（格式不变式只在此处落地）。"""
        for name, value in (('module', self.module),
                            ('resource', self.resource),
                            ('action', self.action)):
            if ':' in value:
                raise InvalidAuditLogException(f'审计 {name} 不允许包含 ":"：{value!r}')
        return self

    @model_validator(mode='after')
    def _check_result_consistency(self):
        """成功不得带错误信息；失败必须有稳定错误码。"""
        if self.result is AuditResultEnum.SUCCESS:
            if self.error_code is not None or self.error_message is not None:
                raise InvalidAuditLogException('成功的审计记录不能带 error_code / error_message')
        elif not self.error_code:
            raise InvalidAuditLogException('失败的审计记录必须提供 error_code')
        return self
