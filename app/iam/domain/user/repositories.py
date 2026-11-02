from abc import abstractmethod
from datetime import datetime

from pydantic import BaseModel

from app.core.domain.repositories import BaseRepository
from app.core.utils.schemas import PageResult
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import Phone, Email, UserId, DeptId, DataScopeSpec
from app.iam.domain.user.entities import User
from app.iam.domain.user.enums import UserTypeEnum


class SearchUser(BaseModel):
    """用户检索条件：文本走单个 `keyword` 模糊；枚举 / 部门 / 时间走精确或区间。

    `deleted=True` = 只看回收站；缺省只看未删。`status` 只筛业务状态（ACTIVE/DISABLED）。
    """
    keyword: str | None = None                          # 跨 username/nickname/email/phone 模糊（icontains）
    user_type: UserTypeEnum | None = None
    status: StatusEnum | None = None
    deleted: bool = False
    dept_id: DeptId | None = None
    need_change_password: bool | None = None            # 筛「未改密码」用户（上线初期用）
    created_at_start: datetime | None = None            # 时间：start/end 各自可选，给哪个用哪个
    created_at_end: datetime | None = None
    password_updated_at_start: datetime | None = None
    password_updated_at_end: datetime | None = None


class UserRepository(BaseRepository[UserId, User]):
    """用户仓储接口"""

    @abstractmethod
    async def get_by_ids(self, user_ids: list[UserId], *,
                         include_deleted: bool = False) -> list[User]: ...

    @abstractmethod
    async def get_by_username(self, username: str, *,
                              include_deleted: bool = False) -> User | None: ...

    # 以下三个 id 查询也遵守「默认不读已删」；唯一性占位判定需显式 include_deleted=True
    @abstractmethod
    async def get_id_by_username(self, username: str, *,
                                 include_deleted: bool = False) -> UserId | None: ...

    @abstractmethod
    async def get_id_by_phone(self, phone: Phone, *,
                              include_deleted: bool = False) -> UserId | None: ...

    @abstractmethod
    async def get_id_by_email(self, email: Email, *,
                              include_deleted: bool = False) -> UserId | None: ...

    @abstractmethod
    async def exists_by_user_type(self, user_type: UserTypeEnum) -> bool: ...

    @abstractmethod
    async def exists_by_dept(self, dept_id: DeptId) -> bool: ...

    @abstractmethod
    async def get_allowed_user_ids(self, current_user: CurrentUser,
                                   include_deleted: bool = False) -> set[UserId]: ...

    @abstractmethod
    async def clear_dept(self, dept_ids: list[DeptId]) -> int:
        """物理清理悬空引用：把这些部门下用户的 dept_id 置空（彻底删除部门时用）。"""
        ...

    @abstractmethod
    async def search(self, search_by: SearchUser, page_size: int, page: int, scope: DataScopeSpec) -> PageResult[
        User]: ...
