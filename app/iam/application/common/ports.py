from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import UserId


class AuditLogIn(BaseModel):
    """iam 应用层的审计写入输入（端口私有 DTO，不是实体）。

    不引用 monitor 的公开 DTO：由 infrastructure 的防腐适配器负责映射。
    """

    resource: str
    action: str
    summary: str

    occurred_at: datetime | None = None

    target_type: str | None = None
    target_id: str | None = None
    target_name: str | None = None

    operator_id: UserId | None = None
    operator_username: str | None = None
    operator_nickname: str | None = None

    success: bool = True
    error_code: str | None = None
    error_message: str | None = None

    request_id: str | None = None
    ip: str | None = None
    user_agent: str | None = None

    detail: dict[str, Any] = Field(default_factory=dict)


def make_audit_log(*, current_user: CurrentUser, resource: str, action: str,
                   summary: str, target_type: str | None = None,
                   target_id: str | None = None, target_name: str | None = None,
                   detail: dict[str, Any] | None = None) -> AuditLogIn:
    """构造审计写入输入，统一带操作人快照。"""
    return AuditLogIn(
        resource=resource,
        action=action,
        summary=summary,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        detail=detail or {},
        operator_id=current_user.user_id,
        operator_username=current_user.username,
        operator_nickname=current_user.nickname,
    )


class AuditLogWriterPort(ABC):
    """审计日志写入端口。

    `write` 不自行开事务：必须在调用方业务事务内执行。
    """

    @abstractmethod
    async def write(self, data: AuditLogIn) -> None: ...
