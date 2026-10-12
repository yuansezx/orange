from pydantic import Field

from app.core.domain.events import BaseEvent
from app.core.domain.value_objects import EventId
from app.iam.domain.shared.value_objects import UserId


class UserRolesChanged(BaseEvent):
    """用户的角色分配变更（授予 / 移除 / 启停）。"""
    id: EventId = Field(default_factory=EventId.new)
    user_id: UserId
