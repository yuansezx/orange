from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class PermissionDeniedException(IAMBusinessBaseException):
    code = 'IAM_PERMISSION_DENIED'
    kind = ErrorKindEnum.FORBIDDEN


class SessionRequiredException(IAMBusinessBaseException):
    """该操作仅限交互式会话（API Key 不能管理凭据/会话等敏感账户操作）。"""
    code = 'IAM_SESSION_REQUIRED'
    kind = ErrorKindEnum.FORBIDDEN


class AuthenticationException(IAMBusinessBaseException):
    code = 'IAM_AUTHENTICATION_FAILED'
    kind = ErrorKindEnum.UNAUTHENTICATED


class InvalidTokenException(AuthenticationException):
    code = 'IAM_INVALID_TOKEN'
