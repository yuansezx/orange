from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.role.entities import Role
from app.iam.domain.shared.value_objects import RoleId, UserId


class RoleRepository(BaseRepository[RoleId, Role]):

    @abstractmethod
    async def get_allowed_role_ids(self, current_user: CurrentUser) -> set[RoleId]: ...
