"""monitor 的组合根：HTTP / bootstrap / python api 共用的 `get_*`。"""
from app.core.infrastructure import persistence
from app.monitor.application.audit_log.services import AuditLogApplicationService
from app.monitor.application.common.ports import AuthenticationPort, SystemInfoPort
from app.monitor.application.system.services import SystemInfoApplicationService
from app.monitor.domain.audit_log.repositories import AuditLogRepository
from app.monitor.infrastructure.adapters.system_info_adapter import SystemInfoAdapter

_repos = persistence.module_infra('monitor', 'repositories')


def get_audit_log_repo() -> AuditLogRepository:
    return _repos.AuditLogRepositoryTortoiseImpl()


def get_authentication() -> AuthenticationPort:
    # 延迟导入：iam 公开 API 会触发 iam 组合根，与 monitor 公开 API 形成模块级循环
    from app.monitor.infrastructure.adapters.authentication_adapter import AuthenticationAdapter
    return AuthenticationAdapter()


def get_audit_log_app_service() -> AuditLogApplicationService:
    return AuditLogApplicationService(audit_log_repo=get_audit_log_repo())


def get_system_info() -> SystemInfoPort:
    return SystemInfoAdapter()


def get_system_info_app_service() -> SystemInfoApplicationService:
    return SystemInfoApplicationService(system_info=get_system_info())
