from abc import ABC, abstractmethod
from datetime import datetime

from app.core.domain.value_objects import EventId


class IdProviderPort[IdType](ABC):
    @abstractmethod
    def generate(self) -> IdType: ...

    @abstractmethod
    def extract_datetime(self,entity_id: IdType) -> datetime: ...

class EventIdProvider(IdProviderPort[EventId]):
    pass