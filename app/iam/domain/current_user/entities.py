from pydantic import BaseModel

from app.iam.domain.shared.value_objects import DataScopeSpec, DeptId, RoleSummary, UserId
from app.iam.domain.user.enums import UserTypeEnum


class CurrentUser(BaseModel):
    user_id: UserId
    username: str
    nickname: str
    user_type: UserTypeEnum
    # 解析好的数据范围（快照构建时算好、随快照缓存；读侧直接用）
    data_scope_spec: DataScopeSpec
    roles: list[RoleSummary] | None = None
    dept_id: DeptId | None = None
    permission_codes: list[str] | None = None

    def has_permission(self, *codes: str) -> bool:
        """是否拥有**全部**给定权限码（`module:resource:action`）。

        超管为逃生舱（不依赖角色分配）、沿用 `can_access` 的旁路约定，恒 True。
        """
        if self.user_type is UserTypeEnum.SUPER_ADMIN:
            return True
        granted = set(self.permission_codes or ())
        return all(code in granted for code in codes)
