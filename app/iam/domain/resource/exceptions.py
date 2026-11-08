from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class InvalidResourceCodeException(IAMBusinessBaseException):
    code = 'IAM_RESOURCE_INVALID_CODE'
    kind = ErrorKindEnum.VALIDATION


class InvalidPermissionActionException(IAMBusinessBaseException):
    code = 'IAM_PERMISSION_INVALID_ACTION'
    kind = ErrorKindEnum.VALIDATION
