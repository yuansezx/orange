from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class ApiKeyNotFoundException(IAMBusinessBaseException):
    code = 'IAM_API_KEY_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND


class ApiKeyScopeNotGrantedException(IAMBusinessBaseException):
    """key 勾选的 scope 超出用户当前有效权限。"""
    code = 'IAM_API_KEY_SCOPE_NOT_GRANTED'
    kind = ErrorKindEnum.VALIDATION


class ApiKeyDataScopeNotAllowedException(IAMBusinessBaseException):
    """key 的 CUSTOM 数据范围超出用户可见部门。"""
    code = 'IAM_API_KEY_DATA_SCOPE_NOT_ALLOWED'
    kind = ErrorKindEnum.VALIDATION


class SuperAdminApiKeyNotAllowedException(IAMBusinessBaseException):
    """超管（逃生舱）不允许持有 API Key。"""
    code = 'IAM_API_KEY_SUPER_ADMIN_NOT_ALLOWED'
    kind = ErrorKindEnum.FORBIDDEN
