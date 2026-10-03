from dataclasses import dataclass
from typing import Self
from uuid import UUID

from future_uuid import uuid7


@dataclass(frozen=True)
class BaseEntityId:
    """实体 ID 值对象：包装 UUID；并在构造时把 str 强制转成 UUID（JWT/路径参数等入口）。"""
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            object.__setattr__(self, 'value', UUID(self.value))

    @classmethod
    def new(cls) -> Self:
        return cls(value=uuid7())

    def __str__(self):
        return str(self.value)


@dataclass(frozen=True)
class EventId(BaseEntityId):
    pass
