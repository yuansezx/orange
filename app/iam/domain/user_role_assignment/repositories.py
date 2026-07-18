from app.core.domain.repositories import BaseRepository
from app.iam.domain.shared.value_objects import UserRoleId, UserId
from app.iam.domain.user_role_assignment.entities import UserRoleAssignment


class UserRoleRepository(BaseRepository[UserRoleId, UserRoleAssignment]):

    async def get_by_user_id(self, user_id: UserId) -> list[UserRoleAssignment]: ...