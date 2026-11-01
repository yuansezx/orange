from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.domain.events import BaseEvent


class OutboxMessage(BaseModel):
    """outbox 中待投递的一条事件（端口内部契约）。"""
    id: UUID
    event_type: str
    payload: dict
    attempts: int


class EventOutboxStore(ABC):
    """生产方 outbox 存储端口。

    `append` 必须加入调用方的业务事务（事件与业务写同库同事务），
    因此 at-least-once 事件只能在 `in_transaction()` 内发布。
    """

    @abstractmethod
    async def append(self, event: BaseEvent) -> None: ...

    @abstractmethod
    async def claim_due(self, limit: int, *, stale_before: datetime) -> list[OutboxMessage]:
        """取一批到期事件并标记为 processing（`FOR UPDATE SKIP LOCKED`）。"""

    @abstractmethod
    async def mark_done(self, message_id: UUID) -> None: ...

    @abstractmethod
    async def mark_failed(self, message_id: UUID, *, error: str, attempts: int,
                          next_attempt_at: datetime, dead: bool) -> None: ...
