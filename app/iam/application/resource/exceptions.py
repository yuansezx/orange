from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class ResourceNotFoundException(IAMBusinessBaseException):
    code = 'IAM_RESOURCE_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND


class PermissionNotFoundException(IAMBusinessBaseException):
    code = 'IAM_PERMISSION_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND


class ResourceCodeConflictException(IAMBusinessBaseException):
    code = 'IAM_RESOURCE_CODE_CONFLICT'
    kind = ErrorKindEnum.CONFLICT


class PermissionActionConflictException(IAMBusinessBaseException):
    code = 'IAM_PERMISSION_ACTION_CONFLICT'
    kind = ErrorKindEnum.CONFLICT
