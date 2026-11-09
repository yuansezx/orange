from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class InvalidRoleCodeException(IAMBusinessBaseException):
    code = 'IAM_ROLE_INVALID_CODE'
    kind = ErrorKindEnum.VALIDATION


class InvalidRoleNameException(IAMBusinessBaseException):
    """角色名不合法（空 / 超长）。"""
    code = 'IAM_ROLE_NAME_INVALID'
    kind = ErrorKindEnum.VALIDATION


class RoleNotDeletedException(IAMBusinessBaseException):
    """对象未处于已删状态：恢复 / 彻底删除的前提不成立。"""
    code = 'IAM_ROLE_NOT_DELETED'
    kind = ErrorKindEnum.CONFLICT
