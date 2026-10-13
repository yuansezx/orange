from app.core.utils.type_utils import to_set
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.dept.entities import Dept
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.shared.value_objects import DeptId
from app.iam.domain.user.enums import UserTypeEnum


def parent_chain(dept: Dept | None) -> set[DeptId]:
    """某部门的「父链」= 自身 ∪ 其祖先 id（None → 空）。

    部门结构变更时，自身部门落在此链上的 DEPT_AND_CHILD 用户会受影响（展开集变化）。
    """
    if dept is None:
        return set()
    return {dept.id, *dept.ancestors}


def shift_descendant_ancestors(descendant_ancestors: list[DeptId], dept_id: DeptId,
                               new_self_ancestors: list[DeptId]) -> list[DeptId]:
    """部门移动后，重算某子孙的 ancestors。

    子孙的原路径形如 `[旧自身祖先..., dept_id, 尾部...]`；移动后前缀换成新自身祖先，
    `dept_id` 及其之后的尾部（到该子孙父级的路径）不变。
    """
    idx = descendant_ancestors.index(dept_id)
    return [*new_self_ancestors, dept_id, *descendant_ancestors[idx + 1:]]


class DeptAccessService:
    def __init__(self, dept_repo: DeptRepository):
        self.dept_repo = dept_repo

    async def can_access(self, dept_ids: DeptId | list[DeptId] | set[DeptId], current_user: CurrentUser) -> bool:
        if current_user.user_type == UserTypeEnum.SUPER_ADMIN:
            return True
        allowed = await self.dept_repo.get_allowed_dept_ids(current_user)
        return to_set(dept_ids).issubset(allowed)
