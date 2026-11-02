from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class ResourceNotFoundException(IAMBusinessBaseException):
    code = 'IAM_RESOURCE_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND


class PermissionNotFoundException(IAMBusinessBaseException):
    code = 'IAM_PERMISSION_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND


class ResourceCodeConflictException(IAMBusinessBaseException):
    code = 'IAM_RESOURCE_CODE_CONFLICT'
    kind = ErrorKindEnum.CONFLICT


class PermissionActionConflictException(IAMBusinessBaseException):
    code = 'IAM_PERMISSION_ACTION_CONFLICT'
    kind = ErrorKindEnum.CONFLICT


class SystemResourceReadOnlyException(IAMBusinessBaseException):
    """SYSTEM = 代码声明拥有；后台只读（否则下次启动会被声明覆盖）。"""
    code = 'IAM_SYSTEM_RESOURCE_READ_ONLY'
    kind = ErrorKindEnum.FORBIDDEN


class SystemPermissionReadOnlyException(IAMBusinessBaseException):
    """SYSTEM = 代码声明拥有；后台只读。"""
    code = 'IAM_SYSTEM_PERMISSION_READ_ONLY'
    kind = ErrorKindEnum.FORBIDDEN


class ResourceNotDeletedException(IAMBusinessBaseException):
    """对象未处于已删状态：恢复 / 彻底删除的前提不成立。"""
    code = 'IAM_RESOURCE_NOT_DELETED'
    kind = ErrorKindEnum.CONFLICT


class PermissionNotDeletedException(IAMBusinessBaseException):
    """对象未处于已删状态：恢复 / 彻底删除的前提不成立。"""
    code = 'IAM_PERMISSION_NOT_DELETED'
    kind = ErrorKindEnum.CONFLICT
