"""审计日志写入的防腐适配器。

iam application 只认识 `AuditLogWriterPort` / `AuditLogIn`；本适配器把本地输入
映射成 monitor 的公开 DTO，再调用 `write_audit_log`。
"""
from app.iam.application.common.ports import AuditLogIn, AuditLogWriterPort
from app.monitor.interface.python.audit_log import (
    AuditLogIn as MonitorAuditLogIn,
    write_audit_log,
)


class AuditLogWriterAdapter(AuditLogWriterPort):

    async def write(self, data: AuditLogIn) -> None:
        await write_audit_log(MonitorAuditLogIn(
            occurred_at=data.occurred_at,
            module='iam',
            resource=data.resource,
            action=data.action,
            summary=data.summary,
            target_type=data.target_type,
            target_id=data.target_id,
            target_name=data.target_name,
            operator_id=data.operator_id.value if data.operator_id else None,
            operator_username=data.operator_username,
            operator_nickname=data.operator_nickname,
            result='success' if data.success else 'failure',
            error_code=data.error_code,
            error_message=data.error_message,
            request_id=data.request_id,
            ip=data.ip,
            user_agent=data.user_agent,
            detail=data.detail,
        ))
