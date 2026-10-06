from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.shared.value_objects import UserId, UserRoleId
from app.iam.domain.user_role_assignment.entities import UserRoleAssignment


class UserRoleRepository(BaseRepository[UserRoleId, UserRoleAssignment]):

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId, include_deleted: bool = False) -> list[UserRoleAssignment]: ...
