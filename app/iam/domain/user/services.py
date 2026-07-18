from app.core.utils.type_utils import to_set
from app.core.utils.validators import check_unique
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import Phone, Email, UserId
from app.iam.domain.user.enums import UserType
from app.iam.domain.user.repositories import UserRepository


class CheckUserUniqueService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def check_username_unique(self, username: str, exclude_user_id: UserId | None = None) -> bool:
        id_to_check = await self.user_repo.get_id_by_username(username)
        return check_unique(id_to_check, exclude_user_id)

    async def check_phone_unique(self, phone: Phone | None, exclude_user_id: UserId | None = None) -> bool:
        if not phone:
            return True
        id_to_check = await self.user_repo.get_id_by_phone(phone)
        return check_unique(id_to_check, exclude_user_id)

    async def check_email_unique(self, email: Email | None, exclude_user_id: UserId | None = None) -> bool:
        if not email:
            return True
        id_to_check = await self.user_repo.get_id_by_email(email)
        return check_unique(id_to_check, exclude_user_id)


class UserAccessService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def can_access(self, user_ids: UserId | list[UserId] | set[UserId], current_user: CurrentUser) -> bool:
        if current_user.user_type == UserType.SUPER_ADMIN:
            return True
        allowed = await self.user_repo.get_allowed_user_ids(current_user)
        return to_set(user_ids).issubset(allowed)