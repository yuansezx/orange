from pydantic import Field

from app.core.domain.events import BaseEvent
from app.core.domain.value_objects import EventId
from app.iam.domain.shared.value_objects import RoleId, UserId


class RoleChanged(BaseEvent):
    """角色（名称 / 状态 / 权限集）变更——持有该角色的用户权限快照需重解析。

    `affected_user_ids`：彻底删除角色时分配行已随角色清掉、事后再查不到持有者，
    故在事务内预取并随事件带出；为 None 时订阅方按 `role_id` 反查。
    """
    id: EventId = Field(default_factory=EventId.new)
    role_id: RoleId
    affected_user_ids: frozenset[UserId] | None = None
