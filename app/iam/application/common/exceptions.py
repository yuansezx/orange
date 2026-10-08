from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class PermissionDeniedException(IAMBusinessBaseException):
    code = 'IAM_PERMISSION_DENIED'
    kind = ErrorKindEnum.FORBIDDEN


class AuthenticationException(IAMBusinessBaseException):
    code = 'IAM_AUTHENTICATION_FAILED'
    kind = ErrorKindEnum.UNAUTHENTICATED


class InvalidTokenException(AuthenticationException):
    code = 'IAM_INVALID_TOKEN'
