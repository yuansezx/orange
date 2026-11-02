from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class UserExistsException(IAMBusinessBaseException):
    code = 'IAM_USER_EXISTS'
    kind = ErrorKindEnum.CONFLICT


class UserNotExistException(IAMBusinessBaseException):
    code = 'IAM_USER_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND


class OldPasswordMismatchException(IAMBusinessBaseException):
    code = 'IAM_OLD_PASSWORD_MISMATCH'
    kind = ErrorKindEnum.VALIDATION


class PasswordResetNotAllowedException(IAMBusinessBaseException):
    """不允许通过管理员重置接口修改自己的密码（应走自助改密）。"""
    code = 'IAM_PASSWORD_RESET_NOT_ALLOWED'
    kind = ErrorKindEnum.CONFLICT


class AvatarValidationException(IAMBusinessBaseException):
    code = 'IAM_AVATAR_INVALID'
    kind = ErrorKindEnum.VALIDATION


class AvatarNotFoundException(IAMBusinessBaseException):
    code = 'IAM_AVATAR_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND
