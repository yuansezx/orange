from abc import ABC, abstractmethod

from app.iam.application.common.dto import EffectivePermissions
from app.iam.domain.shared.value_objects import DeptId, UserId


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
