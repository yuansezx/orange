"""部门结构变更 → 受影响用户的 CQRS 读实现。

user ⊗ user_role ⊗ role 无外键（纯 UUID 列），故不做 join，用若干条索引 values_list
在内存收窄：先定位「自身部门在受影响集内」的用户，再筛「持有 DEPT_AND_CHILD 角色」者。
"""
from app.iam.application.common.queries import UsersAffectedByDeptChangeQuery
from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum
from app.iam.domain.shared.value_objects import DeptId, UserId
from app.iam.infrastructure.persistence.tortoise.postgres.models import (
    RoleModel,
    UserModel,
    UserRoleAssignmentModel,
)


class UsersAffectedByDeptChangeQueryTortoiseImpl(UsersAffectedByDeptChangeQuery):

    async def resolve(self, affected_dept_ids: frozenset[DeptId]) -> set[UserId]:
        if not affected_dept_ids:
            return set()
        dac_role_ids = list(await RoleModel.filter(
            data_scope=DataScopeEnum.DEPT_AND_CHILD, status=StatusEnum.ACTIVE,
            deleted_at__isnull=True,
        ).values_list('id', flat=True))
        if not dac_role_ids:
            return set()
        candidate_user_ids = list(await UserModel.filter(
            dept_id__in=[d.value for d in affected_dept_ids], deleted_at__isnull=True
        ).values_list('id', flat=True))
        if not candidate_user_ids:
            return set()
        hit = await UserRoleAssignmentModel.filter(
            role_id__in=dac_role_ids, user_id__in=candidate_user_ids,
            status=StatusEnum.ACTIVE, deleted_at__isnull=True,
        ).values_list('user_id', flat=True)
        return {UserId(u) for u in hit}
