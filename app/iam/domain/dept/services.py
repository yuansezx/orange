from app.core.utils.type_utils import to_set
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.shared.value_objects import DeptId
from app.iam.domain.user.enums import UserType


class DeptAccessService:
    def __init__(self, dept_repo: DeptRepository):
        self.dept_repo = dept_repo

    async def can_access(self, dept_ids: DeptId | list[DeptId] | set[DeptId], current_user: CurrentUser) -> bool:
        if current_user.user_type == UserType.SUPER_ADMIN:
            return True
        allowed = await self.dept_repo.get_allowed_dept_ids(current_user)
        return to_set(dept_ids).issubset(allowed)
