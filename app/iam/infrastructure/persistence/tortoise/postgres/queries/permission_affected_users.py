"""权限变更影响用户的 CQRS 读实现。

permission → role_permission → user_role（ACTIVE 未删）→ user_id。
只反查仍生效的分配：已停用/已删分配的用户快照本来就不含水印权限，无需失效。
"""
from collections.abc import Iterable

from app.iam.application.common.queries import UsersAffectedByPermissionChangeQuery
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, UserId
from app.iam.infrastructure.persistence.tortoise.postgres.models import (
    RolePermissionModel,
    UserRoleAssignmentModel,
)


class UsersAffectedByPermissionChangeQueryTortoiseImpl(UsersAffectedByPermissionChangeQuery):

    async def resolve(self, permission_ids: Iterable[PermissionId]) -> set[UserId]:
        ids = [p.value for p in permission_ids]
        if not ids:
            return set()
        role_ids = set(await RolePermissionModel.filter(
            permission_id__in=ids).values_list('role_id', flat=True))
        if not role_ids:
            return set()
        user_ids = await UserRoleAssignmentModel.filter(
            role_id__in=list(role_ids),
            status=StatusEnum.ACTIVE,
            deleted_at__isnull=True,
        ).values_list('user_id', flat=True)
        return {UserId(uid) for uid in user_ids}
