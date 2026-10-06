from app.iam.application.common.exceptions import IAMApplicationBaseException


class ResourceNotFoundException(IAMApplicationBaseException):
    pass


class PermissionNotFoundException(IAMApplicationBaseException):
    pass


class ResourceCodeConflictException(IAMApplicationBaseException):
    pass


class PermissionActionConflictException(IAMApplicationBaseException):
    pass
