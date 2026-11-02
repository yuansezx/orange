"""monitor 应用层通用 DTO。"""
from uuid import UUID

from pydantic import BaseModel

from app.monitor.application.common.enums import UserTypeEnum


def _group_codes(group: str | tuple[str, ...]) -> tuple[str, ...]:
    """归一「与组」：裸码 = 单码组，元组 = 多码组。"""
    return (group,) if isinstance(group, str) else group


class CurrentUser(BaseModel):
    """认证后的当前用户（由 iam 的 token → 用户能力映射而来）。

    权限判断在本地完成（分布式模型：iam 只发身份与权限快照），
    语义与 iam 的 `CurrentUser.has_permission` 保持一致。
    """
    user_id: UUID
    username: str
    nickname: str
    user_type: UserTypeEnum
    permission_codes: frozenset[str] = frozenset()

    def has_permission(self, *groups: str | tuple[str, ...]) -> bool:
        """DNF：参数之间「或」，元组内「与」；超管恒真（空参行为与 iam 当前实现一致）。"""
        if self.user_type is UserTypeEnum.SUPER_ADMIN:
            return True
        granted = set(self.permission_codes)
        return any(
            all(code in granted for code in _group_codes(group)) for group in groups
        )
