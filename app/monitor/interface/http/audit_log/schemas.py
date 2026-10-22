"""审计日志 HTTP schema。"""
from app.monitor.application.audit_log.dto import AuditLogOut, GetAuditLogsIn


class GetAuditLogsReq(GetAuditLogsIn):
    """审计日志列表查询参数（线格式同 DTO）。"""


class AuditLogResp(AuditLogOut):
    """审计日志响应。"""
