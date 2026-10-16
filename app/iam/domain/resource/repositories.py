from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.resource.entities import Resource
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId


class ResourceRepository(BaseRepository[ResourceId, Resource]):
    """Resource 聚合仓储（整体装配/保存，连带聚合内权限）。"""

    @abstractmethod
    async def get_by_module_and_code(self, module: str, code: str) -> Resource | None: ...

    @abstractmethod
    async def get_by_permission_id(self, permission_id: PermissionId) -> Resource | None:
        """按**聚合内权限 id** 反查所属资源（后台按权限 id 改/删时用）。"""
        ...

    @abstractmethod
    async def get_all(self, status: StatusEnum | None = None) -> list[Resource]:
        """`status` 缺省 = 全部未删；给了就按该状态过滤（含 `DELETED`，供回收站）。"""
        ...
