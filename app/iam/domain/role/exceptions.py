from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class InvalidRoleCodeException(IAMBusinessBaseException):
    code = 'IAM_INVALID_ROLE_CODE'
    kind = ErrorKindEnum.VALIDATION


class RoleNotDeletedException(IAMBusinessBaseException):
    """对象未处于已删状态：恢复 / 彻底删除的前提不成立。"""
    code = 'IAM_ROLE_NOT_DELETED'
    kind = ErrorKindEnum.CONFLICT
