"""审计日志写入的公开 Python API。"""
from app.monitor.interface.dependences import get_audit_log_app_service
from app.monitor.interface.python.audit_log.schemas import AuditLogReq


async def write_audit_log(record: AuditLogReq) -> None:
    await get_audit_log_app_service().write(record)
