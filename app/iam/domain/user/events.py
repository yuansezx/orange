from pydantic import Field

from app.core.domain.events import BaseEvent
from app.core.domain.value_objects import EventId
from app.iam.domain.shared.value_objects import UserId


class UserChanged(BaseEvent):
    """用户自身属性（昵称 / 部门 / 状态 / 类型等）变更。"""
    id: EventId = Field(default_factory=EventId.new)
    user_id: UserId


class UserHardDeleted(BaseEvent):
    """用户被物理删除（不可恢复）。软删 / 恢复只发 `UserChanged`。"""
    id: EventId = Field(default_factory=EventId.new)
    user_id: UserId
