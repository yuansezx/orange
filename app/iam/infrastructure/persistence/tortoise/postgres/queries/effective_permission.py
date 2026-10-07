"""有效权限解析的 tortoise 实现（CQRS 读侧的查询实现）。

模型间无外键（纯 UUID 列），故不做跨表 join，用若干条索引 values_list 在内存拼装。
逐级过滤 ACTIVE：user_role / role / permission / resource 全须 ACTIVE。
"""
from app.iam.application.common.dto import EffectivePermissions
from app.iam.application.common.queries import EffectivePermissionQuery
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import RoleId, RoleSummary, UserId
from app.iam.infrastructure.persistence.tortoise.postgres.models import (
    PermissionModel,
    ResourceModel,
    RoleModel,
    RolePermissionModel,
    UserRoleAssignmentModel,
)


class EffectivePermissionQueryTortoiseImpl(EffectivePermissionQuery):

    async def resolve(self, user_id: UserId) -> EffectivePermissions:
        # 1) 该用户 ACTIVE 的 user_role 行 → role_id
        link_role_ids = list(await UserRoleAssignmentModel.filter(
            user_id=user_id.value, status=StatusEnum.ACTIVE).values_list('role_id', flat=True))
        if not link_role_ids:
            return EffectivePermissions(frozenset(), frozenset())

        # 2) 必须 ACTIVE 的角色（保住零权限角色）→ (id, code, name)
        role_rows = await RoleModel.filter(
            id__in=link_role_ids, status=StatusEnum.ACTIVE).values_list('id', 'code', 'name')
        role_ids = [rid for rid, _, _ in role_rows]
        roles = frozenset(RoleSummary(id=RoleId(rid), code=code, name=name)
                          for rid, code, name in role_rows)

        # 3) 角色 → 权限 id
        perm_ids = list(await RolePermissionModel.filter(
            role_id__in=role_ids).values_list('permission_id', flat=True))

        # 4) 必须 ACTIVE 的权限 → (resource_id, action)
        rows = await PermissionModel.filter(
            id__in=perm_ids, status=StatusEnum.ACTIVE).values_list('id', 'resource_id', 'action')

        # 5) 必须 ACTIVE 的资源 → (module, code)
        resource_ids = {r[1] for r in rows}
        resource_rows = await ResourceModel.filter(
            id__in=list(resource_ids), status=StatusEnum.ACTIVE).values_list('id', 'module', 'code')
        code_map = {rid: (m, c) for rid, m, c in resource_rows}

        codes = {f'{code_map[rid][0]}:{code_map[rid][1]}:{act}'
                 for _, rid, act in rows if rid in code_map}
        return EffectivePermissions(
            roles=roles,
            permission_codes=frozenset(codes),
        )
