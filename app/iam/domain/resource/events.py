from pydantic import Field

from app.core.domain.events import BaseEvent
from app.core.domain.value_objects import EventId
from app.iam.domain.shared.value_objects import PermissionId, UserId


class ResourceChanged(BaseEvent):
    """资源 / 权限条目变更——持有相关权限的用户快照需重解析。

    `permission_ids`：受影响的权限 id（资源停用/删除时为其权限集）。
    `affected_user_ids`：彻底删除时角色引用行已随权限清掉、事后再查不到持有者，
    故在事务内预取并随事件带出；为 None 时订阅方按权限 id 反查。
    """
    id: EventId = Field(default_factory=EventId.new)
    permission_ids: frozenset[PermissionId] = Field(default_factory=frozenset)
    affected_user_ids: frozenset[UserId] | None = None
