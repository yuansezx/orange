from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class InvalidResourceCodeException(IAMBusinessBaseException):
    code = 'IAM_RESOURCE_INVALID_CODE'
    kind = ErrorKindEnum.VALIDATION


class InvalidPermissionActionException(IAMBusinessBaseException):
    code = 'IAM_PERMISSION_INVALID_ACTION'
    kind = ErrorKindEnum.VALIDATION


class InvalidResourceNameException(IAMBusinessBaseException):
    """资源名不合法（空 / 超长）。"""
    code = 'IAM_RESOURCE_NAME_INVALID'
    kind = ErrorKindEnum.VALIDATION


class InvalidPermissionNameException(IAMBusinessBaseException):
    """权限名不合法（空 / 超长）。"""
    code = 'IAM_PERMISSION_NAME_INVALID'
    kind = ErrorKindEnum.VALIDATION
