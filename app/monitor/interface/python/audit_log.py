"""审计日志写入的公开 Python API。

其他模块在 infrastructure 适配器里调用 `write_audit_log`，且必须处于业务事务内：
审计行随业务一起提交/回滚。
"""
from app.monitor.application.audit_log.dto import AuditLogIn
from app.monitor.interface.dependences import get_audit_log_app_service

__all__ = ['AuditLogIn', 'write_audit_log']


async def write_audit_log(record: AuditLogIn) -> None:
    await get_audit_log_app_service().write(record)
