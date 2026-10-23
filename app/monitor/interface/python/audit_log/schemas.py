"""审计日志写入的公开 schema（接口层契约）。

当前字段与应用层 DTO 一致，用空子类留出契约缝隙。
"""
from app.monitor.application.audit_log.dto import AuditLogIn as _AuditLogIn


class AuditLogReq(_AuditLogIn):
    """公开 API 的审计写入入参。"""
