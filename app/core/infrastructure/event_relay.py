import asyncio
from datetime import datetime, UTC, timedelta

from loguru import logger

from app.core.domain.event_bus import EventTransport
from app.core.domain.event_outbox import EventOutboxStore, OutboxMessage
from app.core.domain.events import BaseEvent
from app.core.infrastructure.event_bus_impl import EventBusImpl
from app.core.infrastructure.settings import EventsConfig


class LocalEventTransport(EventTransport):
    """进程内订阅者通道：交给 EventBusImpl.dispatch_local。"""

    def __init__(self, bus: EventBusImpl) -> None:
        self._bus = bus

    async def deliver(self, event: BaseEvent) -> None:
        await self._bus.dispatch_local(event)


class EventRelay:
    """轮询各生产模块的 outbox，把事件投递给 transports。

    当前只挂 `LocalEventTransport`；webhook / broker 作为新的 EventTransport
    加入即可，生产者和消费者代码不变。
    """

    def __init__(self, bus: EventBusImpl, transports: list[EventTransport],
                 config: EventsConfig) -> None:
        self._bus = bus
        self._transports = transports
        self._config = config
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run(), name='event-relay')
            logger.info('事件 relay 已启动（poll={}s）',
                        self._config.relay_poll_interval_seconds)

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        while True:
            try:
                await self.tick()
            except Exception:
                logger.exception('事件 relay 轮询失败')
            await asyncio.sleep(self._config.relay_poll_interval_seconds)

    async def tick(self) -> None:
        stale_before = datetime.now(UTC) - timedelta(
            seconds=self._config.relay_lock_timeout_seconds)
        for store in self._bus.outbox_stores():
            try:
                messages = await store.claim_due(
                    self._config.relay_batch_size, stale_before=stale_before)
            except Exception:
                logger.exception('事件 outbox 取事件失败：{}', type(store).__name__)
                continue
            for message in messages:
                await self._deliver(store, message)

    async def _deliver(self, store: EventOutboxStore, message: OutboxMessage) -> None:
        event_type = self._bus.event_class_for(message.event_type)
        if event_type is None:
            await self._dead_letter(store, message, f'未知事件类型：{message.event_type}')
            return

        try:
            event = event_type.model_validate(message.payload)
        except Exception as exc:
            await self._dead_letter(store, message, f'事件反序列化失败：{exc}')
            return

        try:
            for transport in self._transports:
                await transport.deliver(event)
        except Exception as exc:
            await self._retry_or_dead(store, message, exc)
            return

        await store.mark_done(message.id)

    async def _dead_letter(self, store: EventOutboxStore, message: OutboxMessage,
                           error: str) -> None:
        await store.mark_failed(
            message.id,
            error=error,
            attempts=self._config.relay_max_attempts,
            next_attempt_at=datetime.now(UTC),
            dead=True,
        )
        logger.error('事件进入死信：{} (id={})：{}', message.event_type, message.id, error)

    async def _retry_or_dead(self, store: EventOutboxStore, message: OutboxMessage,
                             exc: Exception) -> None:
        attempts = message.attempts + 1
        dead = attempts >= self._config.relay_max_attempts
        delay = min(
            self._config.relay_retry_base_seconds * (2 ** message.attempts),
            self._config.relay_retry_max_seconds,
        )
        await store.mark_failed(
            message.id,
            error=str(exc),
            attempts=attempts,
            next_attempt_at=datetime.now(UTC) + timedelta(seconds=delay),
            dead=dead,
        )
        if dead:
            logger.error('事件投递失败，进入死信：{} (id={})', message.event_type, message.id)
        else:
            logger.warning('事件投递失败，{}s 后重试：{} (id={})',
                           delay, message.event_type, message.id)
