import asyncio
from collections import defaultdict

from loguru import logger

from app.core.domain.event_bus import EventBus, EventHandler
from app.core.domain.event_outbox import EventOutboxStore
from app.core.domain.events import BaseEvent, EventDeliveryEnum, event_type_name


class EventBusImpl(EventBus):
    """事件总线实现。

    - `best_effort`：publish 时后台派发（强引用保活、异常只记日志）。
    - `at_least_once`：publish 只把事件写入生产方 outbox（须在业务事务内），
      由 `EventRelay` 取事件、经 `EventTransport` 投递；进程内订阅者也走 relay。

    消费者只通过 `subscribe` 注册，不需要知道投递实现。
    """

    def __init__(self) -> None:
        self._handlers: dict[type[BaseEvent], list[EventHandler]] = defaultdict(list)
        self._outboxes: dict[type[BaseEvent], EventOutboxStore] = {}
        self._event_types: dict[str, type[BaseEvent]] = {}
        self._tasks: set[asyncio.Task] = set()

    def subscribe(self, event_type: type[BaseEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def register_outbox(self, event_type: type[BaseEvent],
                        store: EventOutboxStore) -> None:
        """模块 bootstrap 登记本模块可靠事件对应的 outbox store。"""
        self._outboxes[event_type] = store
        self._event_types[event_type_name(event_type)] = event_type

    async def publish(self, event: BaseEvent) -> None:
        if event.delivery is EventDeliveryEnum.AT_LEAST_ONCE:
            store = self._outboxes.get(type(event))
            if store is None:
                raise RuntimeError(f'事件 {event_type_name(type(event))} 未注册 outbox')
            await store.append(event)
            return
        self._dispatch_in_background(event)

    def event_class_for(self, type_name: str) -> type[BaseEvent] | None:
        return self._event_types.get(type_name)

    def outbox_stores(self) -> list[EventOutboxStore]:
        # 同一 store 可注册多个事件，按实例去重
        return list(dict.fromkeys(self._outboxes.values()))

    async def dispatch_local(self, event: BaseEvent) -> None:
        """同步分发给进程内订阅者；由 relay 的本地 transport 调用（异常向上抛以触发重试）。"""
        for handler in list(self._handlers.get(type(event), [])):
            await handler.handle(event)

    def _dispatch_in_background(self, event: BaseEvent) -> None:
        for handler in list(self._handlers.get(type(event), [])):
            task = asyncio.create_task(self._run_handler(handler, event))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    async def _run_handler(self, handler: EventHandler, event: BaseEvent) -> None:
        try:
            await handler.handle(event)
        except Exception:
            logger.exception('best-effort 事件处理失败：{}', event_type_name(type(event)))
