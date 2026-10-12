from pydantic import Field

from app.core.domain.events import BaseEvent
from app.core.domain.value_objects import EventId
from app.iam.domain.shared.value_objects import UserId


class UserChanged(BaseEvent):
    """用户自身属性（昵称 / 部门 / 状态 / 类型等）变更。"""
    id: EventId = Field(default_factory=EventId.new)
    user_id: UserId
