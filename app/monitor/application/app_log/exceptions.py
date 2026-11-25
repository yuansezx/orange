"""应用日志应用层异常。"""
from app.core.exceptions import ErrorKindEnum
from app.monitor.domain.shared.exceptions import MonitorBusinessBaseException


class MonitorAppLogArchiveDisabledException(MonitorBusinessBaseException):
    code = 'MONITOR_APP_LOG_ARCHIVE_DISABLED'
    kind = ErrorKindEnum.CONFLICT


class MonitorAppLogFileInvalidException(MonitorBusinessBaseException):
    code = 'MONITOR_APP_LOG_FILE_INVALID'
    kind = ErrorKindEnum.VALIDATION


class MonitorAppLogFileNotFoundException(MonitorBusinessBaseException):
    code = 'MONITOR_APP_LOG_FILE_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND
