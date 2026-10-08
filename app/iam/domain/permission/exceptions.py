from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class InvalidPermissionActionException(IAMBusinessBaseException):
    code = 'IAM_INVALID_PERMISSION_ACTION'
    kind = ErrorKindEnum.VALIDATION
