"""monitor 的组合根：HTTP / bootstrap / python api 共用的 `get_*`。

后续 outbox relay、审计查询应用服务也在此装配。
"""
from app.core.infrastructure import persistence
from app.monitor.domain.audit_log.repositories import AuditLogRepository

_repos = persistence.module_infra('monitor', 'repositories')


def get_audit_log_repo() -> AuditLogRepository:
    return _repos.AuditLogRepositoryTortoiseImpl()
