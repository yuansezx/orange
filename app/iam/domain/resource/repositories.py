from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.resource.entities import Resource
from app.iam.domain.shared.value_objects import ResourceId


class ResourceRepository(BaseRepository[ResourceId, Resource]):

    @abstractmethod
    async def get_by_module_and_code(self, module: str, code: str) -> Resource | None: ...

    @abstractmethod
    async def get_all(self) -> list[Resource]: ...
