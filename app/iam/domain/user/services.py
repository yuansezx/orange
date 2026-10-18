from app.core.utils.type_utils import to_set
from app.core.utils.validators import check_unique
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import Phone, Email, UserId
from app.iam.domain.user.enums import UserTypeEnum
from app.iam.domain.user.repositories import UserRepository


class CheckUserUniqueService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def check_username_unique(self, username: str, exclude_user_id: UserId | None = None) -> bool:
        # 软删仍占位：唯一性判定必须把已删行算进来
        id_to_check = await self.user_repo.get_id_by_username(username, include_deleted=True)
        return check_unique(id_to_check, exclude_user_id)

    async def check_phone_unique(self, phone: Phone | None, exclude_user_id: UserId | None = None) -> bool:
        if not phone:
            return True
        id_to_check = await self.user_repo.get_id_by_phone(phone, include_deleted=True)
        return check_unique(id_to_check, exclude_user_id)

    async def check_email_unique(self, email: Email | None, exclude_user_id: UserId | None = None) -> bool:
        if not email:
            return True
        id_to_check = await self.user_repo.get_id_by_email(email, include_deleted=True)
        return check_unique(id_to_check, exclude_user_id)


class UserAccessService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def can_access(self, user_ids: UserId | list[UserId] | set[UserId], current_user: CurrentUser,
                         *, include_deleted: bool = False) -> bool:
        """`include_deleted` = 回收站场景（恢复 / 彻底删除）也按数据范围判定。"""
        if current_user.user_type == UserTypeEnum.SUPER_ADMIN:
            return True
        allowed = await self.user_repo.get_allowed_user_ids(current_user, include_deleted)
        return to_set(user_ids).issubset(allowed)