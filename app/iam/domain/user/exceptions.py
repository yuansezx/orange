from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class PasswordPolicyViolationException(IAMBusinessBaseException):
    code = 'IAM_PASSWORD_POLICY_VIOLATION'
    kind = ErrorKindEnum.VALIDATION


class UserProfileValidationException(IAMBusinessBaseException):
    """自助资料字段不合法（如昵称为空）。"""
    code = 'IAM_USER_PROFILE_INVALID'
    kind = ErrorKindEnum.VALIDATION


class UserImmutableException(IAMBusinessBaseException):
    """目标用户不可更改/删除（SYSTEM / SUPER_ADMIN 等受保护账户，与调用者权限无关）。"""
    code = 'IAM_USER_IMMUTABLE'
    kind = ErrorKindEnum.CONFLICT


class ReservedUsernameException(IAMBusinessBaseException):
    code = 'IAM_RESERVED_USERNAME'
    kind = ErrorKindEnum.VALIDATION


class UserNotDeletedException(IAMBusinessBaseException):
    """对象未处于已删状态：恢复 / 彻底删除的前提不成立。"""
    code = 'IAM_USER_NOT_DELETED'
    kind = ErrorKindEnum.CONFLICT


class SuperAdminSelfDisableException(IAMBusinessBaseException):
    """超管不能停用自己——否则可能失去唯一能恢复系统的账号（死档）。"""
    code = 'IAM_SUPER_ADMIN_SELF_DISABLE'
    kind = ErrorKindEnum.CONFLICT
