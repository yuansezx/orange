from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class UserExistsException(IAMBusinessBaseException):
    code = 'IAM_USER_EXISTS'
    kind = ErrorKindEnum.CONFLICT


class UserNotExistException(IAMBusinessBaseException):
    code = 'IAM_USER_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND
