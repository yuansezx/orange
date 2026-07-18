from app.iam.domain.shared.exceptions import IAMDomainBaseException


class PasswordPolicyViolationException(IAMDomainBaseException):
    pass

class UserUpdateForbiddenException(IAMDomainBaseException):
    pass