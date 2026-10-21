from app.core.exceptions import ErrorKindEnum
from app.monitor.domain.shared.exceptions import MonitorBusinessBaseException


class InvalidAuditLogException(MonitorBusinessBaseException):
    code = 'MONITOR_INVALID_AUDIT_LOG'
    kind = ErrorKindEnum.VALIDATION
