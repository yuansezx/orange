"""iam 对外 Python API 的认证 schema。"""
from pydantic import BaseModel

from app.iam.domain.shared.value_objects import DataScopeSpec, DeptId, RoleSummary, UserId
from app.iam.domain.user.enums import UserTypeEnum


class CurrentUserResp(BaseModel):
    """认证后的当前用户视图；消费方据此在本地做功能/数据权限判断。"""
    user_id: UserId
    username: str
    nickname: str
    user_type: UserTypeEnum
    data_scope_spec: DataScopeSpec
    roles: list[RoleSummary] | None = None
    dept_id: DeptId | None = None
    permission_codes: list[str] | None = None
