from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class InvalidResourceCodeException(IAMBusinessBaseException):
    code = 'IAM_INVALID_RESOURCE_CODE'
    kind = ErrorKindEnum.VALIDATION
