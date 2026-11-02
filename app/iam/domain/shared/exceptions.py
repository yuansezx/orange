from app.core.exceptions import BusinessBaseException


class IAMBusinessBaseException(BusinessBaseException):
    """iam 业务异常根——domain 与 application 共用（不再分两棵树）。"""
