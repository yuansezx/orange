from dataclasses import dataclass

from app.iam.domain.shared.value_objects import RoleSummary


@dataclass(frozen=True)
class EffectivePermissions:
    """某用户「有效」的角色与权限（逐级按 ACTIVE 过滤后的结果）。"""
    roles: frozenset[RoleSummary]
    permission_codes: frozenset[str]  # module:resource:action
