from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.resource.entities import Resource
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId


class ResourceRepository(BaseRepository[ResourceId, Resource]):
    """Resource 聚合仓储（整体装配/保存，连带聚合内权限）。"""

    @abstractmethod
    async def get_by_module_and_code(self, module: str, code: str, *,
                                     include_deleted: bool = False,
                                     include_deleted_permissions: bool = False) -> Resource | None:
        """按自然键取聚合。声明/占位判定需显式含已删（含聚合内权限）。"""
        ...

    @abstractmethod
    async def get_by_permission_id(self, permission_id: PermissionId, *,
                                   include_deleted: bool = False) -> Resource | None:
        """按**聚合内权限 id** 反查所属资源（后台按权限 id 改/删时用）。"""
        ...

    @abstractmethod
    async def get_all(self, status: StatusEnum | None = None, deleted: bool = False,
                      include_deleted_permissions: bool = False) -> list[Resource]:
        """`deleted=False` 只看未删、`True` 只看回收站；`status` 只筛业务状态。

        聚合内权限默认只装配未删的；声明/回收站确需全量时显式置位。
        """
        ...

    @abstractmethod
    async def get_by_module(self, module: str, *, include_deleted: bool = False,
                            include_deleted_permissions: bool = False) -> list[Resource]:
        """按模块取聚合（对账 pass 用；`include_deleted=True` 含已删）。"""
        ...

    @abstractmethod
    async def hard_delete_permission(self, permission_id: PermissionId) -> int:
        """物理删聚合内单条权限（仅限已软删；调用方先清角色引用）。"""
        ...
