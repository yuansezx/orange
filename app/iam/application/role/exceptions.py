from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class RoleNotFoundException(IAMBusinessBaseException):
    code = 'IAM_ROLE_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND


class RoleCodeConflictException(IAMBusinessBaseException):
    code = 'IAM_ROLE_CODE_CONFLICT'
    kind = ErrorKindEnum.CONFLICT
