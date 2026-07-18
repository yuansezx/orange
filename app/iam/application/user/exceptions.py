from app.iam.application.common.exceptions import IAMApplicationBaseException


class UserExistsException(IAMApplicationBaseException):
    pass

class UserNotExistException(IAMApplicationBaseException):
    pass