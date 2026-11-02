from datetime import datetime, UTC
from uuid import UUID

from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from app.core.domain.event_outbox import EventOutboxStore, OutboxMessage
from app.core.domain.events import BaseEvent, event_type_name
from app.core.infrastructure.persistence.tortoise.models import (
    EventOutboxModel,
    OutboxStatusEnum,
)


class TortoiseEventOutboxStore(EventOutboxStore):
    """基于生产模块提供的事件 outbox 表模型（表随模块迁移）。"""

    def __init__(self, model: type[EventOutboxModel]) -> None:
        self._model = model
        self._connection = model._meta.default_connection

    async def append(self, event: BaseEvent) -> None:
        # 调用方须在业务事务内；tortoise 会把该写并入当前 task 的事务连接
        await self._model.create(
            id=event.id.value,
            event_type=event_type_name(type(event)),
            payload=event.model_dump(mode='json'),
            occurred_at=event.created_at,
            status=OutboxStatusEnum.PENDING,
            attempts=0,
            next_attempt_at=datetime.now(UTC),
        )

    async def claim_due(self, limit: int, *, stale_before: datetime) -> list[OutboxMessage]:
        now = datetime.now(UTC)
        async with in_transaction(self._connection):
            rows = await self._model.filter(
                Q(status=OutboxStatusEnum.PENDING)
                | Q(status=OutboxStatusEnum.PROCESSING, locked_at__lt=stale_before),
                next_attempt_at__lte=now,
            ).order_by('next_attempt_at', 'id').limit(limit).select_for_update(skip_locked=True)
            if rows:
                await self._model.filter(id__in=[row.id for row in rows]).update(
                    status=OutboxStatusEnum.PROCESSING, locked_at=now)
        return [
            OutboxMessage(
                id=row.id,
                event_type=row.event_type,
                payload=row.payload,
                attempts=row.attempts,
            )
            for row in rows
        ]

    async def mark_done(self, message_id: UUID) -> None:
        await self._model.filter(id=message_id).update(
            status=OutboxStatusEnum.DONE,
            processed_at=datetime.now(UTC),
            locked_at=None,
        )

    async def mark_failed(self, message_id: UUID, *, error: str, attempts: int,
                          next_attempt_at: datetime, dead: bool) -> None:
        await self._model.filter(id=message_id).update(
            status=OutboxStatusEnum.DEAD if dead else OutboxStatusEnum.PENDING,
            attempts=attempts,
            next_attempt_at=next_attempt_at,
            last_error=error[:2000],
            locked_at=None,
        )
