from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class InvalidRoleCodeException(IAMBusinessBaseException):
    code = 'IAM_INVALID_ROLE_CODE'
    kind = ErrorKindEnum.VALIDATION
