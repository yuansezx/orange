from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class DeptNotFoundException(IAMBusinessBaseException):
    code = 'IAM_DEPT_NOT_FOUND'
    kind = ErrorKindEnum.NOT_FOUND


class DeptParentUnavailableException(IAMBusinessBaseException):
    """上级部门不存在 / 已删除 / 已停用。"""
    code = 'IAM_DEPT_PARENT_UNAVAILABLE'
    kind = ErrorKindEnum.VALIDATION


class DeptNameConflictException(IAMBusinessBaseException):
    """同一上级下部门名重复。"""
    code = 'IAM_DEPT_NAME_CONFLICT'
    kind = ErrorKindEnum.CONFLICT


class DeptHasUsersException(IAMBusinessBaseException):
    """部门下存在用户，不允许删除。"""
    code = 'IAM_DEPT_HAS_USERS'
    kind = ErrorKindEnum.CONFLICT
