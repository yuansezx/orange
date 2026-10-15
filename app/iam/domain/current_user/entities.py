from pydantic import BaseModel

from app.iam.domain.shared.value_objects import DataScopeSpec, DeptId, RoleSummary, UserId
from app.iam.domain.user.enums import UserTypeEnum


def _group_codes(group: str | tuple[str, ...]) -> tuple[str, ...]:
    """归一「与组」：裸码 = 单码组，元组 = 多码组。"""
    return (group,) if isinstance(group, str) else group


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

    def has_permission(self, *groups: str | tuple[str, ...]) -> bool:
        """功能权限判定（DNF）：**逗号分隔的参数之间「或」；元组内的权限码之间「与」**。

        例（码形如 `module:resource:action`）：
          `has_permission('a', 'b')`            ⇔ a ∨ b
          `has_permission(('a', 'b'), 'c')`     ⇔ (a ∧ b) ∨ c
          `has_permission('a')`                 ⇔ a

        **空参恒 True**（空真：「拥有全部 0 个权限」）。此与 `requires_permission` 的
        「空参报错」**有意不对称**——谓词问「是否满足要求」，闸门表达「这是一条要求」。

        超管为逃生舱（不依赖角色分配）、沿用 `can_access` 的旁路约定，恒 True。
        """
        if self.user_type is UserTypeEnum.SUPER_ADMIN:
            return True
        granted = set(self.permission_codes or ())
        return any(
            all(code in granted for code in _group_codes(group)) for group in groups
        )
