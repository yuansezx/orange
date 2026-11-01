from datetime import datetime, UTC
from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, Field

from app.core.domain.value_objects import EventId


class EventDeliveryEnum(str, Enum):
    """事件投递保证。

    BEST_EFFORT：进程内派发，可丢（如缓存失效）。
    AT_LEAST_ONCE：生产方 outbox 持久化 + relay 投递，不可丢（如跨模块数据清理）。
    """
    BEST_EFFORT = 'best_effort'
    AT_LEAST_ONCE = 'at_least_once'


class BaseEvent(BaseModel):
    id: EventId
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    delivery: ClassVar[EventDeliveryEnum] = EventDeliveryEnum.BEST_EFFORT


def event_type_name(event_type: type[BaseEvent]) -> str:
    """事件持久化/跨进程传输用的类型名（模块路径 + 类名）。"""
    return f'{event_type.__module__}.{event_type.__qualname__}'
