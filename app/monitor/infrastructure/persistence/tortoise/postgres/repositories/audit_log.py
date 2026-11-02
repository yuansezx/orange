from datetime import datetime

from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from app.core.exceptions import PersistenceException
from app.monitor.domain.audit_log.entities import AuditLog
from app.monitor.domain.audit_log.enums import AuditResultEnum
from app.monitor.domain.audit_log.repositories import AuditLogRepository
from app.monitor.domain.shared.value_objects import AuditLogId, OperatorId
from app.monitor.infrastructure.persistence.tortoise.postgres.models import AuditLogModel


def _to_domain(m: AuditLogModel) -> AuditLog:
    return AuditLog(
        id=AuditLogId(m.id),
        occurred_at=m.occurred_at,
        module=m.module,
        resource=m.resource,
        action=m.action,
        summary=m.summary,
        target_type=m.target_type,
        target_id=m.target_id,
        target_name=m.target_name,
        operator_id=OperatorId(m.operator_id) if m.operator_id else None,
        operator_username=m.operator_username,
        operator_nickname=m.operator_nickname,
        result=m.result,
        error_code=m.error_code,
        error_message=m.error_message,
        request_id=m.request_id,
        ip=m.ip,
        user_agent=m.user_agent,
        detail=m.detail or {},
    )


def _apply_filters(qs: QuerySet[AuditLogModel], *,
                   module: str | None,
                   resource: str | None,
                   action: str | None,
                   operator_id: OperatorId | None,
                   operator_username: str | None,
                   target_type: str | None,
                   target_id: str | None,
                   result: AuditResultEnum | None,
                   request_id: str | None,
                   keyword: str | None,
                   occurred_from: datetime | None,
                   occurred_to: datetime | None) -> QuerySet[AuditLogModel]:
    if module is not None:
        qs = qs.filter(module=module)
    if resource is not None:
        qs = qs.filter(resource=resource)
    if action is not None:
        qs = qs.filter(action=action)
    if operator_id is not None:
        qs = qs.filter(operator_id=operator_id.value)
    if operator_username is not None:
        qs = qs.filter(operator_username__icontains=operator_username)
    if target_type is not None:
        qs = qs.filter(target_type=target_type)
    if target_id is not None:
        qs = qs.filter(target_id=target_id)
    if result is not None:
        qs = qs.filter(result=result)
    if request_id is not None:
        qs = qs.filter(request_id=request_id)
    if keyword is not None:
        qs = qs.filter(
            Q(summary__icontains=keyword)
            | Q(target_name__icontains=keyword)
            | Q(operator_username__icontains=keyword)
            | Q(error_message__icontains=keyword)
            | Q(request_id__icontains=keyword)
        )
    if occurred_from is not None:
        qs = qs.filter(occurred_at__gte=occurred_from)
    if occurred_to is not None:
        qs = qs.filter(occurred_at__lte=occurred_to)
    return qs


class AuditLogRepositoryTortoiseImpl(AuditLogRepository):

    async def create(self, audit_log: AuditLog) -> AuditLog:
        try:
            await AuditLogModel.create(
                id=audit_log.id.value,
                occurred_at=audit_log.occurred_at,
                module=audit_log.module,
                resource=audit_log.resource,
                action=audit_log.action,
                summary=audit_log.summary,
                target_type=audit_log.target_type,
                target_id=audit_log.target_id,
                target_name=audit_log.target_name,
                operator_id=audit_log.operator_id.value if audit_log.operator_id else None,
                operator_username=audit_log.operator_username,
                operator_nickname=audit_log.operator_nickname,
                result=audit_log.result,
                error_code=audit_log.error_code,
                error_message=audit_log.error_message,
                request_id=audit_log.request_id,
                ip=audit_log.ip,
                user_agent=audit_log.user_agent,
                detail=audit_log.detail,
            )
        except Exception as exc:
            raise PersistenceException('审计日志写入失败') from exc
        return audit_log

    async def get_all(self, *,
                      module: str | None = None,
                      resource: str | None = None,
                      action: str | None = None,
                      operator_id: OperatorId | None = None,
                      operator_username: str | None = None,
                      target_type: str | None = None,
                      target_id: str | None = None,
                      result: AuditResultEnum | None = None,
                      request_id: str | None = None,
                      keyword: str | None = None,
                      occurred_from: datetime | None = None,
                      occurred_to: datetime | None = None,
                      offset: int = 0,
                      limit: int = 50) -> list[AuditLog]:
        qs = _apply_filters(
            AuditLogModel.all(),
            module=module, resource=resource, action=action,
            operator_id=operator_id, operator_username=operator_username,
            target_type=target_type, target_id=target_id,
            result=result, request_id=request_id, keyword=keyword,
            occurred_from=occurred_from, occurred_to=occurred_to,
        )
        # occurred_at 相同用 UUIDv7 兜底，保证分页稳定且与入队顺序一致
        models = await qs.order_by('-occurred_at', '-id').offset(offset).limit(limit)
        return [_to_domain(m) for m in models]

    async def count(self, *,
                    module: str | None = None,
                    resource: str | None = None,
                    action: str | None = None,
                    operator_id: OperatorId | None = None,
                    operator_username: str | None = None,
                    target_type: str | None = None,
                    target_id: str | None = None,
                    result: AuditResultEnum | None = None,
                    request_id: str | None = None,
                    keyword: str | None = None,
                    occurred_from: datetime | None = None,
                    occurred_to: datetime | None = None) -> int:
        qs = _apply_filters(
            AuditLogModel.all(),
            module=module, resource=resource, action=action,
            operator_id=operator_id, operator_username=operator_username,
            target_type=target_type, target_id=target_id,
            result=result, request_id=request_id, keyword=keyword,
            occurred_from=occurred_from, occurred_to=occurred_to,
        )
        return await qs.count()
