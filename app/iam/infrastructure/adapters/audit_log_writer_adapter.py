"""审计日志写入的防腐适配器。

port 只认识调用方上下文；本适配器负责：
- 操作人快照（`CurrentUser` → `operator_*`）；
- 请求元数据（`RequestMeta` → `request_id` / `ip` / `user_agent`）；
- 映射成 monitor 的公开 DTO 并调用 `write_audit_log`。
"""
from typing import Any

from app.core.application.dto import RequestMeta
from app.iam.application.common.ports import AuditLogWriterPort
from app.iam.domain.current_user.entities import CurrentUser
from app.monitor.interface.python.audit_log import (
    AuditLogReq as MonitorAuditLogReq,
    write_audit_log,
)


class AuditLogWriterAdapter(AuditLogWriterPort):

    async def write(self, *,
                    resource: str, action: str, summary: str,
                    current_user: CurrentUser | None = None,
                    request_meta: RequestMeta | None = None,
                    target_type: str | None = None,
                    target_id: str | None = None,
                    target_name: str | None = None,
                    detail: dict[str, Any] | None = None,
                    success: bool = True,
                    error_code: str | None = None,
                    error_message: str | None = None) -> None:
        await write_audit_log(MonitorAuditLogReq(
            module='iam',
            resource=resource,
            action=action,
            summary=summary,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            operator_id=current_user.user_id if current_user else None,
            operator_username=current_user.username if current_user else None,
            operator_nickname=current_user.nickname if current_user else None,
            result='success' if success else 'failure',
            error_code=error_code,
            error_message=error_message,
            request_id=request_meta.request_id if request_meta else None,
            ip=request_meta.ip if request_meta else None,
            user_agent=request_meta.user_agent if request_meta else None,
            detail=detail or {},
        ))
