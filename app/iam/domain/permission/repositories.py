from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.permission.entities import Permission
from app.iam.domain.shared.value_objects import PermissionId, ResourceId


class PermissionRepository(BaseRepository[PermissionId, Permission]):

    @abstractmethod
    async def get_by_resource_and_action(self, resource_id: ResourceId, action: str) -> Permission | None: ...

    @abstractmethod
    async def get_by_resource_ids(self, resource_ids: list[ResourceId]) -> list[Permission]: ...

    @abstractmethod
    async def get_by_ids(self, permission_ids: list[PermissionId]) -> list[Permission]: ...
