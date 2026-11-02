from app.core.exceptions import BusinessBaseException


class MonitorBusinessBaseException(BusinessBaseException):
    """monitor 业务异常根——domain 与 application 共用。"""
