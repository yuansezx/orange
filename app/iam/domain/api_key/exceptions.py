from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class InvalidApiKeyNameException(IAMBusinessBaseException):
    """API Key 名称不合法（空 / 超长）。"""
    code = 'IAM_API_KEY_NAME_INVALID'
    kind = ErrorKindEnum.VALIDATION


class InvalidApiKeyTokenException(IAMBusinessBaseException):
    """令牌摘要 / 展示提示格式不合法。"""
    code = 'IAM_API_KEY_TOKEN_INVALID'
    kind = ErrorKindEnum.VALIDATION


class InvalidApiKeyScopeException(IAMBusinessBaseException):
    """权限子集为空，或权限码不是 `module:resource:action` 形式。"""
    code = 'IAM_API_KEY_SCOPE_INVALID'
    kind = ErrorKindEnum.VALIDATION


class InvalidApiKeyDataScopeException(IAMBusinessBaseException):
    """数据范围限制不合法（kind 不支持 / CUSTOM 缺部门 / 非 CUSTOM 带部门）。"""
    code = 'IAM_API_KEY_DATA_SCOPE_INVALID'
    kind = ErrorKindEnum.VALIDATION


class InvalidApiKeyExpiryException(IAMBusinessBaseException):
    """过期时间不合法（必须带时区）。"""
    code = 'IAM_API_KEY_EXPIRY_INVALID'
    kind = ErrorKindEnum.VALIDATION
