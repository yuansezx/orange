from app.core.exceptions import ErrorKindEnum
from app.monitor.domain.shared.exceptions import MonitorBusinessBaseException


class InvalidAuditLogException(MonitorBusinessBaseException):
    code = 'MONITOR_AUDIT_LOG_INVALID'
    kind = ErrorKindEnum.VALIDATION
