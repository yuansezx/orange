from datetime import datetime, UTC

from app.core.utils.schemas import PageResult
from app.iam.application.common.decorators import requires_permission
from app.iam.domain.current_user.entities import CurrentUser
from app.monitor.application.audit_log.dto import AuditLogIn, AuditLogOut, GetAuditLogsIn
from app.monitor.domain.audit_log.entities import AuditLog
from app.monitor.domain.audit_log.repositories import AuditLogRepository
from app.monitor.domain.shared.value_objects import AuditLogId


def _to_out(log: AuditLog) -> AuditLogOut:
    return AuditLogOut(
        id=log.id,
        occurred_at=log.occurred_at,
        module=log.module,
        resource=log.resource,
        action=log.action,
        key=log.full_code,
        summary=log.summary,
        target_type=log.target_type,
        target_id=log.target_id,
        target_name=log.target_name,
        operator_id=log.operator_id,
        operator_username=log.operator_username,
        operator_nickname=log.operator_nickname,
        result=log.result,
        error_code=log.error_code,
        error_message=log.error_message,
        request_id=log.request_id,
        ip=log.ip,
        user_agent=log.user_agent,
        detail=log.detail,
    )


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

    @requires_permission('monitor:audit_log:read')
    async def get_page(self, data: GetAuditLogsIn,
                       current_user: CurrentUser) -> PageResult[AuditLogOut]:
        filters = dict(
            module=data.module,
            resource=data.resource,
            action=data.action,
            operator_id=data.operator_id,
            target_type=data.target_type,
            target_id=data.target_id,
            result=data.result,
            request_id=data.request_id,
            occurred_from=data.occurred_from,
            occurred_to=data.occurred_to,
        )
        total = await self.audit_log_repo.count(**filters)
        logs = await self.audit_log_repo.get_all(
            **filters,
            offset=(data.page - 1) * data.page_size,
            limit=data.page_size,
        )
        return PageResult(
            page=data.page,
            page_size=data.page_size,
            total=total,
            data=[_to_out(log) for log in logs],
        )
