from app.core.utils.type_utils import to_set
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.role.repositories import RoleRepository
from app.iam.domain.shared.value_objects import RoleId
from app.iam.domain.user.enums import UserType


class RoleAccessService:
    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo

    async def can_access(self, role_ids: RoleId | list[RoleId] | set[RoleId], current_user: CurrentUser) -> bool:
        if current_user.user_type == UserType.SUPER_ADMIN:
            return True
        allowed = await self.role_repo.get_allowed_role_ids(current_user)
        return to_set(role_ids).issubset(allowed)
