"""monitor 应用层通用异常。"""
from app.core.exceptions import ErrorKindEnum
from app.monitor.domain.shared.exceptions import MonitorBusinessBaseException


class MonitorPermissionDeniedException(MonitorBusinessBaseException):
    code = 'MONITOR_PERMISSION_DENIED'
    kind = ErrorKindEnum.FORBIDDEN


class MonitorUnauthenticatedException(MonitorBusinessBaseException):
    code = 'MONITOR_UNAUTHENTICATED'
    kind = ErrorKindEnum.UNAUTHENTICATED
