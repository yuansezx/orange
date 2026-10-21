"""monitor 的组合根：HTTP / bootstrap / python api 共用的 `get_*`。"""
from app.core.infrastructure import persistence
from app.monitor.application.audit_log.services import AuditLogApplicationService
from app.monitor.domain.audit_log.repositories import AuditLogRepository

_repos = persistence.module_infra('monitor', 'repositories')


def get_audit_log_repo() -> AuditLogRepository:
    return _repos.AuditLogRepositoryTortoiseImpl()


def get_audit_log_app_service() -> AuditLogApplicationService:
    return AuditLogApplicationService(audit_log_repo=get_audit_log_repo())
