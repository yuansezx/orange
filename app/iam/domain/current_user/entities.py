from pydantic import BaseModel, ConfigDict, Field

from app.iam.domain.shared.enums import AuthMethodEnum
from app.iam.domain.shared.value_objects import (
    ApiKeyId,
    DataScopeSpec,
    DeptSummary,
    RoleSummary,
    UserId,
)
from app.iam.domain.user.enums import UserTypeEnum


def _group_codes(group: str | tuple[str, ...]) -> tuple[str, ...]:
    """归一「与组」：裸码 = 单码组，元组 = 多码组。"""
    return (group,) if isinstance(group, str) else group


class AuthContext(BaseModel):
    """单次认证的上下文（来源 / 凭证）。

    不是用户属性，**不随用户快照缓存**；由认证入口按本次请求附加。
    """
    model_config = ConfigDict(frozen=True)

    method: AuthMethodEnum
    api_key_id: ApiKeyId | None = None
    api_key_name: str | None = None


class CurrentUser(BaseModel):
    user_id: UserId
    username: str
    nickname: str
    user_type: UserTypeEnum
    # 解析好的数据范围（快照构建时算好、随快照缓存；读侧直接用）
    data_scope_spec: DataScopeSpec
    roles: list[RoleSummary] | None = None
    # 所属部门快照：id + 名称 + 祖先链（供展示与 dept_and_child 可见性判定）。
    # 必填（可为 None）：旧快照缺该字段时解析失败，按缓存未命中重建。
    dept: DeptSummary | None
    avatar_key: str | None = None
    permission_codes: list[str] | None = None
    # 单次认证上下文：每请求不同，序列化时排除（不进用户快照）
    auth: AuthContext | None = Field(default=None, exclude=True)

    def has_permission(self, *groups: str | tuple[str, ...]) -> bool:
        """功能权限判定（DNF）：**逗号分隔的参数之间「或」；元组内的权限码之间「与」**。

        例（码形如 `module:resource:action`）：
          `has_permission('a', 'b')`            ⇔ a ∨ b
          `has_permission(('a', 'b'), 'c')`     ⇔ (a ∧ b) ∨ c
          `has_permission('a')`                 ⇔ a

        空参不是有效要求：`requires_permission` 在定义期拒绝空参，本谓词对空参返回 False。
        谓词问「是否满足要求」，闸门表达「这是一条要求」。

        超管为逃生舱（不依赖角色分配）、沿用 `can_access` 的旁路约定，恒 True。
        """
        if self.user_type is UserTypeEnum.SUPER_ADMIN:
            return True
        granted = set(self.permission_codes or ())
        return any(
            all(code in granted for code in _group_codes(group)) for group in groups
        )
