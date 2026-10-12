from app.core.exceptions import ErrorKindEnum
from app.iam.domain.shared.exceptions import IAMBusinessBaseException


class DeptCycleException(IAMBusinessBaseException):
    """上级部门不能是自己或自己的下级（移动会形成环）。"""
    code = 'IAM_DEPT_CYCLE'
    kind = ErrorKindEnum.VALIDATION
