from pydantic import Field

from app.core.domain.events import BaseEvent
from app.core.domain.value_objects import EventId
from app.iam.domain.shared.value_objects import RoleId


class RoleChanged(BaseEvent):
    """角色（名称 / 状态 / 权限集）变更——持有该角色的用户权限快照需重解析。"""
    id: EventId = Field(default_factory=EventId.new)
    role_id: RoleId
