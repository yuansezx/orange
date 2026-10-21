from datetime import datetime, UTC

from app.monitor.application.audit_log.dto import AuditLogIn
from app.monitor.domain.audit_log.entities import AuditLog
from app.monitor.domain.audit_log.repositories import AuditLogRepository
from app.monitor.domain.shared.value_objects import AuditLogId


class AuditLogApplicationService:
    """审计写入用例。

    `write` **不自行开事务**：必须由调用方在业务事务内执行。
    同库时“业务成功 ⇒ 审计写入、业务回滚 ⇒ 审计一并回滚”。
    """

    def __init__(self, audit_log_repo: AuditLogRepository) -> None:
        self.audit_log_repo = audit_log_repo

    async def write(self, data: AuditLogIn) -> None:
        audit_log = AuditLog(
            id=AuditLogId.new(),
            occurred_at=data.occurred_at or datetime.now(UTC),
            module=data.module,
            resource=data.resource,
            action=data.action,
            summary=data.summary,
            target_type=data.target_type,
            target_id=data.target_id,
            target_name=data.target_name,
            operator_id=data.operator_id,
            operator_username=data.operator_username,
            operator_nickname=data.operator_nickname,
            result=data.result,
            error_code=data.error_code,
            error_message=data.error_message,
            request_id=data.request_id,
            ip=data.ip,
            user_agent=data.user_agent,
            detail=data.detail,
        )
        await self.audit_log_repo.create(audit_log)
