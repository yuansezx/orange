from abc import ABC, abstractmethod
from datetime import datetime

from app.core.domain.value_objects import EventId


class IdProvider[IdType](ABC):
    @abstractmethod
    def generate(self) -> IdType: ...

    @abstractmethod
    def extract_datetime(self,entity_id: IdType) -> datetime: ...

class EventIdProvider(IdProvider[EventId]):
    pass