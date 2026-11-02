from enum import Enum


# ==================== 技术中立异常 ====================

class InfrastructureBaseException(Exception):
    """技术中立异常根。

    基础层负责「库异常 → 本族中立异常」；跨边界**禁止**抛第三方库类型。
    兜底就是本类本身；某个关切真实到需要单独 catch/定位时，才加子类。
    """


class PersistenceException(InfrastructureBaseException):
    """数据存储（DB/ORM）失败——待真实需要时落实现。"""


class CacheException(InfrastructureBaseException):
    """缓存失败——待真实需要时落实现。"""


# ==================== 业务异常 ====================

class ErrorKindEnum(str, Enum):
    """业务错误的语义类别——**传输无关**；与 HTTP 状态码的映射在接口层。"""
    VALIDATION = 'VALIDATION'
    UNAUTHENTICATED = 'UNAUTHENTICATED'
    FORBIDDEN = 'FORBIDDEN'
    NOT_FOUND = 'NOT_FOUND'
    CONFLICT = 'CONFLICT'


class BusinessBaseException(Exception):
    """业务异常根（domain 与 application 共用）。

    - ``code``：类级，稳定机读码（前端/调用方契约），具体异常按需覆盖；
    - ``kind``：类级，语义类别，决定 HTTP 状态码（缺省 VALIDATION → 400）；
    - ``details``：实例级可选结构化补充（如字段级校验信息）。
    """
    code: str = 'BUSINESS_ERROR'
    kind: ErrorKindEnum = ErrorKindEnum.VALIDATION

    def __init__(self, message: str = '', details=None):
        super().__init__(message)
        self.details = details
