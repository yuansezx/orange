from app.iam.application.common.exceptions import IAMApplicationBaseException


class RoleNotFoundException(IAMApplicationBaseException):
    pass


class RoleCodeConflictException(IAMApplicationBaseException):
    pass
