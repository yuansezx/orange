from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel

from app.iam.domain.shared.value_objects import DeptId, RoleSummary


@dataclass(frozen=True)
class EffectivePermissions:
    """某用户「有效」的角色与权限（逐级按 ACTIVE 过滤后的结果）。"""
    roles: frozenset[RoleSummary]
    permission_codes: frozenset[str]  # module:resource:action


class AuditOut(BaseModel):
    """审计信息（平铺）：创建 / 更新 / 删除的时间与人。未发生/未设置 → None。"""
    created_at: datetime
    created_by_username: str | None = None
    created_by_nickname: str | None = None
    updated_at: datetime | None = None
    updated_by_username: str | None = None
    updated_by_nickname: str | None = None
    deleted_at: datetime | None = None
    deleted_by_username: str | None = None
    deleted_by_nickname: str | None = None


class DeptRefOut(BaseModel):
    """部门引用（读侧展示）：id + 名称 + 层级路径（根→自身）。"""
    id: DeptId
    name: str
    path: str
