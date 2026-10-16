from abc import ABC, abstractmethod

from app.iam.application.common.dto import EffectivePermissions
from app.iam.domain.shared.value_objects import DeptId, PermissionId, UserId


class EffectivePermissionQuery(ABC):
    """有效权限解析的**唯一收口**：user_id → 有效角色集 + 权限标识集。

    跨聚合只读查询（CQRS 读侧，属应用层）。逐级过滤 ACTIVE：
    user_role / role / permission / resource 全须 ACTIVE。
    """

    @abstractmethod
    async def resolve(self, user_id: UserId) -> EffectivePermissions: ...


class UsersAffectedByDeptChangeQuery(ABC):
    """部门结构变更 → 数据范围会变、需失效快照的用户（CQRS 读侧）。

    = 自身部门落在受影响集内 且 持有 ACTIVE 的 `data_scope=DEPT_AND_CHILD` 角色 的用户。
    """

    @abstractmethod
    async def resolve(self, affected_dept_ids: frozenset[DeptId]) -> set[UserId]: ...


class PermissionExistsQuery(ABC):
    """按 id 过滤出**存在**的权限（CQRS 读侧，角色分配权限时校验用）。

    permission 是 Resource 聚合内实体、无独立仓储，跨聚合读故走此查询。
    """

    @abstractmethod
    async def filter_existing(self, permission_ids: list[PermissionId]) -> set[PermissionId]: ...
