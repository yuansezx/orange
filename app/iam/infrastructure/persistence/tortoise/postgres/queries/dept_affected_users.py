"""部门结构变更 → 受影响用户的 CQRS 读实现。

快照含 `data_scope_spec` 与 `dept.ancestors`：前者只有 DEPT_AND_CHILD 角色会变，
后者对部门子树内的**所有用户**都会变。故直接返回受影响部门内的全部用户，
宁可多清（清缓存幂等），避免祖先链过期。
"""
from app.iam.application.common.queries import UsersAffectedByDeptChangeQuery
from app.iam.domain.shared.value_objects import DeptId, UserId
from app.iam.infrastructure.persistence.tortoise.postgres.models import UserModel


class UsersAffectedByDeptChangeQueryTortoiseImpl(UsersAffectedByDeptChangeQuery):

    async def resolve(self, affected_dept_ids: frozenset[DeptId]) -> set[UserId]:
        if not affected_dept_ids:
            return set()
        user_ids = await UserModel.filter(
            dept_id__in=[d.value for d in affected_dept_ids],
            deleted_at__isnull=True,
        ).values_list('id', flat=True)
        return {UserId(u) for u in user_ids}
