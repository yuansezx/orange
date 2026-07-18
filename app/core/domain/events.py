from datetime import datetime, UTC

from pydantic import BaseModel, Field

from app.core.domain.value_objects import EventId


class BaseEvent(BaseModel):
    id: EventId
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))