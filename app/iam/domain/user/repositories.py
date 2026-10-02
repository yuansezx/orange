from abc import abstractmethod
from datetime import datetime

from pydantic import BaseModel

from app.core.domain.repositories import BaseRepository
from app.core.utils.schemas import PageResult
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import Phone, Email, UserId, DeptId
from app.iam.domain.user.entities import User
from app.iam.domain.user.enums import UserTypeEnum


class SearchUser(BaseModel):
    username: str | None
    nickname: str | None
    email: str | None = None
    phone: Phone | None = None
    user_type: UserTypeEnum | None = None
    status: StatusEnum | None = None
    need_change_password: bool | None = None
    password_updated_at_between: tuple[datetime, datetime] | None = None
    remark: str | None = None
    dept_id: DeptId | None = None
    created_at_between: tuple[datetime, datetime] | None = None


class UserRepository(BaseRepository[UserId, User]):
    """用户仓储接口"""

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def get_id_by_username(self, username: str) -> UserId | None: ...

    @abstractmethod
    async def get_id_by_phone(self, phone: Phone) -> UserId | None: ...

    @abstractmethod
    async def get_id_by_email(self, email: Email) -> UserId | None: ...

    @abstractmethod
    async def get_allowed_user_ids(self, current_user: CurrentUser) -> set[UserId]: ...

    @abstractmethod
    async def search(self, search_by: SearchUser, page_size: int, page: int, current_user: CurrentUser) -> PageResult[
        User]: ...
