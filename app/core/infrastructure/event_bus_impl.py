
import asyncio
from collections import defaultdict
from app.core.domain.event_bus import EventBus, EventHandler
from app.core.domain.events import BaseEvent


class EventBusMemoryImpl(EventBus):
    def __init__(self):
        self._handlers: dict[type[BaseEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type, handler):
        self._handlers[event_type].append(handler)

    async def publish(self, event):
        for handler in self._handlers.get(type(event), []):
            asyncio.create_task(handler.handle(event))
