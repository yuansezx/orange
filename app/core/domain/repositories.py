from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

EntityType = TypeVar("EntityType", bound=BaseModel)


class BaseRepository[IdType, EntityType](ABC):
    @abstractmethod
    async def get(self, entity_id: IdType) -> EntityType | None: ...

    @abstractmethod
    async def create(self, entity: EntityType) -> EntityType: ...

    @abstractmethod
    async def bulk_create(self, entities: list[EntityType]): ...

    @abstractmethod
    async def update(self, entity: EntityType) -> EntityType: ...

    @abstractmethod
    async def hard_delete(self, entity_ids: IdType | list[IdType]) -> int: ...
