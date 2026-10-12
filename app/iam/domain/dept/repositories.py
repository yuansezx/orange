from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.dept.entities import Dept
from app.iam.domain.shared.value_objects import DeptId


class DeptRepository(BaseRepository[DeptId, Dept]):

    @abstractmethod
    async def get_all(self, include_deleted: bool = False) -> list[Dept]: ...

    @abstractmethod
    async def get_descendants(self, dept_id: DeptId) -> list[Dept]:
        """返回 dept_id 的全部子孙（不含自己、不含已删）。走 ancestors 的 GIN 索引。"""
        ...

    @abstractmethod
    async def has_children(self, dept_id: DeptId) -> bool: ...

    @abstractmethod
    async def get_by_parent_and_name(self, parent_id: DeptId | None, name: str) -> Dept | None: ...

    @abstractmethod
    async def get_allowed_dept_ids(self, current_user: CurrentUser) -> set[DeptId]: ...
