from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class DeptCycleException(IAMBusinessBaseException):
    """上级部门不能是自己或自己的下级（移动会形成环）。"""
    code = 'IAM_DEPT_CYCLE'
    kind = ErrorKindEnum.VALIDATION


class DeptNotDeletedException(IAMBusinessBaseException):
    """对象未处于已删状态：恢复 / 彻底删除的前提不成立。"""
    code = 'IAM_DEPT_NOT_DELETED'
    kind = ErrorKindEnum.CONFLICT
