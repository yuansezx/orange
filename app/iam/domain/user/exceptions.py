from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class PasswordPolicyViolationException(IAMBusinessBaseException):
    code = 'IAM_PASSWORD_POLICY_VIOLATION'
    kind = ErrorKindEnum.VALIDATION


class UserImmutableException(IAMBusinessBaseException):
    """目标用户不可更改/删除（SYSTEM / SUPER_ADMIN 等受保护账户，与调用者权限无关）。"""
    code = 'IAM_USER_IMMUTABLE'
    kind = ErrorKindEnum.CONFLICT


class ReservedUsernameException(IAMBusinessBaseException):
    code = 'IAM_RESERVED_USERNAME'
    kind = ErrorKindEnum.VALIDATION
