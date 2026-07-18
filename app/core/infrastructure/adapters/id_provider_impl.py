from datetime import datetime, UTC

import future_uuid as uuid
from app.core.domain.ports import EventIdProvider
from app.core.domain.value_objects import EventId


class EventIdProviderUUID7Impl(EventIdProvider):
    def generate(self) -> EventId:
        return EventId(value=str(uuid.uuid7()))

    def extract_datetime(self, entity_id: EventId) -> datetime:
        uuid_obj = uuid.UUID(entity_id.value)
        timestamp_ms = uuid_obj.int >> 80
        return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)