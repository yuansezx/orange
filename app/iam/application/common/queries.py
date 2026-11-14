from abc import ABC, abstractmethod
from collections.abc import Iterable

from app.iam.application.common.dto import EffectivePermissions
from app.iam.domain.shared.value_objects import DeptId, PermissionId, UserId


class EffectivePermissionQuery(ABC):
    """有效权限解析的**唯一收口**：user_id → 有效角色集 + 权限标识集。

    跨聚合只读查询（CQRS 读侧，属应用层）。逐级过滤「未删且 ACTIVE」：
    user_role / role / permission / resource 全须满足。
    """

    @abstractmethod
    async def resolve(self, user_id: UserId) -> EffectivePermissions: ...


class UsersAffectedByDeptChangeQuery(ABC):
    """部门变更 → 需失效快照的用户（CQRS 读侧）。

    快照含 `data_scope_spec` 与 `dept.ancestors/name`，两者都可能因部门变更而变；
    直接返回受影响部门内的**全部用户**（宁可多清，清缓存幂等）。
    """

    @abstractmethod
    async def resolve(self, affected_dept_ids: frozenset[DeptId]) -> set[UserId]: ...


class PermissionExistsQuery(ABC):
    """按 id 过滤出**存在**的权限（CQRS 读侧，角色分配权限时校验用）。

    permission 是 Resource 聚合内实体、无独立仓储，跨聚合读故走此查询。
    """

    @abstractmethod
    async def filter_existing(self, permission_ids: list[PermissionId]) -> set[PermissionId]: ...


class UsersAffectedByPermissionChangeQuery(ABC):
    """权限条目（状态 / 删除 / 恢复）变更 → 快照需失效的用户（CQRS 读侧）。

    = 通过角色持有这些权限、且用户角色分配仍 ACTIVE 未删的用户。
    """

    @abstractmethod
    async def resolve(self, permission_ids: Iterable[PermissionId]) -> set[UserId]: ...
