from app.core.exceptions import ApplicationBaseException


class IAMApplicationBaseException(ApplicationBaseException):
    pass


class PermissionDeniedException(IAMApplicationBaseException):
    pass