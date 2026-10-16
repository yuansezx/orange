"""权限 id 存在性校验的 CQRS 读实现（跨聚合只读）。

permission 现为 Resource 聚合内实体、无独立仓储，故直接查表（排除软删）。
"""
from app.iam.application.common.queries import PermissionExistsQuery
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId
from app.iam.infrastructure.persistence.tortoise.postgres.models import PermissionModel


class PermissionExistsQueryTortoiseImpl(PermissionExistsQuery):

    async def filter_existing(self, permission_ids: list[PermissionId]) -> set[PermissionId]:
        if not permission_ids:
            return set()
        found = await PermissionModel.filter(
            id__in=[p.value for p in permission_ids], status__not=StatusEnum.DELETED
        ).values_list('id', flat=True)
        return {PermissionId(i) for i in found}
