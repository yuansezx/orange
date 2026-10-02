from app.core.exceptions import ApplicationBaseException


class IAMApplicationBaseException(ApplicationBaseException):
    pass


class PermissionDeniedException(IAMApplicationBaseException):
    pass

class OperationNotAllowedException(IAMApplicationBaseException):
    pass

class AuthenticationException(IAMApplicationBaseException):
    pass

class InvalidTokenException(AuthenticationException):
    pass

