from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.shared.value_objects import RoleId, UserId, UserRoleId
from app.iam.domain.user_role_assignment.entities import UserRoleAssignment


class UserRoleRepository(BaseRepository[UserRoleId, UserRoleAssignment]):

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId, include_deleted: bool = False) -> list[UserRoleAssignment]: ...

    @abstractmethod
    async def get_user_ids_by_role(self, role_id: RoleId) -> list[UserId]:
        """持有该角色的用户（ACTIVE 分配）——角色变动时扇出失效用。"""
        ...

    @abstractmethod
    async def hard_delete_by_user(self, user_id: UserId) -> int:
        """物理清理悬空引用：删掉该用户的全部角色分配（彻底删除用户时用）。"""
        ...

    @abstractmethod
    async def hard_delete_by_role(self, role_id: RoleId) -> int:
        """物理清理悬空引用：删掉该角色的全部分配（彻底删除角色时用）。"""
        ...
