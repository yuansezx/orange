from abc import ABC, abstractmethod

from app.iam.application.common.dto import EffectivePermissions
from app.iam.domain.shared.value_objects import UserId


class EffectivePermissionQuery(ABC):
    """有效权限解析的**唯一收口**：user_id → 有效角色集 + 权限标识集。

    跨聚合只读查询（CQRS 读侧，属应用层）。逐级过滤 ACTIVE：
    user_role / role / permission / resource 全须 ACTIVE。
    """

    @abstractmethod
    async def resolve(self, user_id: UserId) -> EffectivePermissions: ...
