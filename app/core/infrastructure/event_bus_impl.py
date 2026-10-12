
import asyncio
from collections import defaultdict
from app.core.domain.event_bus import EventBus, EventHandler
from app.core.domain.events import BaseEvent


class EventBusMemoryImpl(EventBus):
    """进程内事件总线（**临时实现**）。

    `publish` 用 `create_task` 派发 = **fire-and-forget**：不等 handler 完成、不传播其异常；
    且事件循环对 Task 只持弱引用（未保活时可能中途被 GC，导致事件偶发丢失）。以上均为
    **已知取舍、暂不修**——后续预期接入消息系统（broker）承载事件派发，届时 `publish` 只需
    把事件交给 broker（投递由 broker 保证），本实现随之被替换。
    """

    def __init__(self):
        self._handlers: dict[type[BaseEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type, handler):
        self._handlers[event_type].append(handler)

    async def publish(self, event):
        for handler in self._handlers.get(type(event), []):
            asyncio.create_task(handler.handle(event))
