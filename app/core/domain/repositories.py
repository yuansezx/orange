from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

EntityType = TypeVar("EntityType", bound=BaseModel)


class BaseRepository[IdType, EntityType](ABC):
    @abstractmethod
    async def get(self, entity_id: IdType, *, include_deleted: bool = False) -> EntityType | None:
        """按 id 取实体。**默认不返回软删对象**；回收站等确需已删时显式 `include_deleted=True`。"""
        ...

    @abstractmethod
    async def create(self, entity: EntityType) -> EntityType: ...

    @abstractmethod
    async def bulk_create(self, entities: list[EntityType]): ...

    @abstractmethod
    async def update(self, entity: EntityType) -> EntityType: ...

    @abstractmethod
    async def hard_delete(self, entity_ids: IdType | list[IdType]) -> int: ...
