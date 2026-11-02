from abc import ABC, abstractmethod

from app.core.domain.events import BaseEvent


class EventHandler(ABC):
    @abstractmethod
    async def handle(self, event: BaseEvent): ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: BaseEvent): ...

    @abstractmethod
    def subscribe(self, event_type: type[BaseEvent], handler: EventHandler): ...


class EventTransport(ABC):
    """事件投递通道。进程内订阅者、webhook、broker 都实现本接口。"""

    @abstractmethod
    async def deliver(self, event: BaseEvent): ...
