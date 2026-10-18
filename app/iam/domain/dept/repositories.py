from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.dept.entities import Dept
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, UserId


class DeptRepository(BaseRepository[DeptId, Dept]):

    @abstractmethod
    async def get_all(self, status: StatusEnum | None = None, deleted: bool = False) -> list[Dept]:
        """`deleted=False` 只看未删、`True` 只看回收站；`status` 只筛业务状态。"""
        ...

    @abstractmethod
    async def get_descendants(self, dept_id: DeptId, include_deleted: bool = False) -> list[Dept]:
        """返回 dept_id 的全部子孙（不含自己；缺省不含已删）。走 ancestors 的 GIN 索引。"""
        ...

    @abstractmethod
    async def get_by_parent_and_name(self, parent_id: DeptId | None, name: str, *,
                                     include_deleted: bool = False) -> Dept | None:
        """同级同名查。唯一性占位需显式 `include_deleted=True`（软删仍占名）。"""
        ...

    @abstractmethod
    async def get_by_ids(self, dept_ids: list[DeptId], *,
                         include_deleted: bool = False) -> list[Dept]: ...

    @abstractmethod
    async def get_allowed_dept_ids(self, current_user: CurrentUser,
                                   include_deleted: bool = False) -> set[DeptId]: ...

    @abstractmethod
    async def clear_leader(self, user_id: UserId) -> int:
        """物理清理悬空引用：把负责人为该用户的部门 leader_id 置空（彻底删除用户时用）。"""
        ...
