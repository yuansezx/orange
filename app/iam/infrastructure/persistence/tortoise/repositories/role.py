"""Role 聚合的 tortoise 仓储实现（整体装配/保存角色 + 权限集/部门集）。

聚合跨三表：iam_role（本体）+ iam_role_permission / iam_role_dept（关系集合）。
get/get_all 装配完整聚合；create/update/hard_delete 整体落库；关系集合差集替换。
"""
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.role.entities import Role
from app.iam.domain.role.repositories import RoleRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, PermissionId, RoleId, UserId
from app.iam.infrastructure.persistence.tortoise.models import (
    RoleDeptModel,
    RoleModel,
    RolePermissionModel,
)


def to_domain(m: RoleModel) -> Role:
    return Role(
        id=RoleId(m.id),
        code=m.code,
        name=m.name,
        data_scope=m.data_scope,
        status=m.status,
        description=m.description,
        created_at=m.created_at,
        created_by=UserId(m.created_by),
        updated_at=m.updated_at,
        updated_by=UserId(m.updated_by) if m.updated_by else None,
        deleted_at=m.deleted_at,
        deleted_by=UserId(m.deleted_by) if m.deleted_by else None,
    )


def to_model_fields(r: Role) -> dict:
    """领域实体 → 表模型字段字典（只覆盖 iam_role 的列；关系集合另行落库）。"""
    return dict(
        id=r.id.value,
        code=r.code,
        name=r.name,
        data_scope=r.data_scope,
        status=r.status,
        description=r.description,
        created_at=r.created_at,
        created_by=r.created_by.value,
        updated_at=r.updated_at,
        updated_by=r.updated_by.value if r.updated_by else None,
        deleted_at=r.deleted_at,
        deleted_by=r.deleted_by.value if r.deleted_by else None,
    )


def _assemble(m: RoleModel, perms: dict, depts: dict) -> Role:
    role = to_domain(m)
    role.permission_ids = perms.get(m.id, set())
    role.custom_dept_ids = depts.get(m.id, set())
    return role


async def _replace_links(model, column: str, role_id, target: set) -> None:
    """差集替换某角色在关系表里的集合（裸表物理删）。"""
    current = set(await model.filter(role_id=role_id).values_list(column, flat=True))
    to_remove = current - target
    to_add = target - current
    if to_remove:
        await model.filter(role_id=role_id, **{f'{column}__in': list(to_remove)}).delete()
    if to_add:
        await model.bulk_create([model(role_id=role_id, **{column: v}) for v in to_add])


class RoleRepositoryTortoiseImpl(RoleRepository):

    # ---------------- 读（整体装配） ----------------
    async def get(self, entity_id: RoleId) -> Role | None:
        m = await RoleModel.get_or_none(id=entity_id.value)
        if m is None:
            return None
        perms, depts = await self._load_relations([m.id])
        return _assemble(m, perms, depts)

    async def get_by_code(self, code: str) -> Role | None:
        m = await RoleModel.get_or_none(code=code)
        if m is None:
            return None
        perms, depts = await self._load_relations([m.id])
        return _assemble(m, perms, depts)

    async def get_all(self, include_deleted: bool = False) -> list[Role]:
        qs = RoleModel.all()
        if not include_deleted:
            qs = qs.filter(status__not=StatusEnum.DELETED)
        models = await qs.order_by('code')
        if not models:
            return []
        perms, depts = await self._load_relations([m.id for m in models])
        return [_assemble(m, perms, depts) for m in models]

    # ---------------- 写（整体保存） ----------------
    async def create(self, entity: Role) -> Role:
        await RoleModel.create(**to_model_fields(entity))
        await self._write_relations(entity)
        return entity

    async def bulk_create(self, entities: list[Role]) -> list[Role]:
        if not entities:
            return []
        await RoleModel.bulk_create([RoleModel(**to_model_fields(e)) for e in entities])
        perm_rows = [RolePermissionModel(role_id=e.id.value, permission_id=p.value)
                     for e in entities for p in e.permission_ids]
        dept_rows = [RoleDeptModel(role_id=e.id.value, dept_id=d.value)
                     for e in entities for d in e.custom_dept_ids]
        if perm_rows:
            await RolePermissionModel.bulk_create(perm_rows)
        if dept_rows:
            await RoleDeptModel.bulk_create(dept_rows)
        return entities

    async def update(self, entity: Role) -> Role:
        fields = to_model_fields(entity)
        fields.pop('id')  # 主键不参与更新
        await RoleModel.filter(id=entity.id.value).update(**fields)
        await self._write_relations(entity)  # 差集替换关系集合
        return entity

    async def hard_delete(self, entity_ids: RoleId | list[RoleId]) -> int:
        ids = [i.value for i in entity_ids] if isinstance(entity_ids, list) else [entity_ids.value]
        await RolePermissionModel.filter(role_id__in=ids).delete()
        await RoleDeptModel.filter(role_id__in=ids).delete()
        return await RoleModel.filter(id__in=ids).delete()

    # ---------------- 数据权限（待 user_role） ----------------
    async def get_allowed_role_ids(self, current_user: CurrentUser) -> set[RoleId]:
        # TODO: 数据权限——依赖 user_role 等表，待其落地后实现
        raise NotImplementedError('角色数据权限查询待 user_role 表落地后实现')

    # ---------------- 内部 ----------------
    async def _load_relations(self, role_ids: list) -> tuple[dict, dict]:
        perms: dict = {}
        rows = await RolePermissionModel.filter(role_id__in=role_ids).values_list('role_id', 'permission_id')
        for rid, pid in rows:
            perms.setdefault(rid, set()).add(PermissionId(pid))
        depts: dict = {}
        rows = await RoleDeptModel.filter(role_id__in=role_ids).values_list('role_id', 'dept_id')
        for rid, did in rows:
            depts.setdefault(rid, set()).add(DeptId(did))
        return perms, depts

    async def _write_relations(self, role: Role) -> None:
        rid = role.id.value
        await _replace_links(RolePermissionModel, 'permission_id', rid, {p.value for p in role.permission_ids})
        await _replace_links(RoleDeptModel, 'dept_id', rid, {d.value for d in role.custom_dept_ids})
