from dataclasses import dataclass


@dataclass(frozen=True)
class BaseEntityId:
    value: str

    def __str__(self):
        return self.value

@dataclass(frozen=True)
class EventId(BaseEntityId):
    pass