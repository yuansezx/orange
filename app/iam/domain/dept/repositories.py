from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.dept.entities import Dept
from app.iam.domain.shared.value_objects import DeptId, UserId


class DeptRepository(BaseRepository[DeptId, Dept]):

    @abstractmethod
    async def get_allowed_dept_ids(self, current_user: CurrentUser) -> set[DeptId]: ...
