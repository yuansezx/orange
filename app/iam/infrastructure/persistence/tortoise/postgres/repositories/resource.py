"""Resource 聚合的 tortoise 仓储实现（整体装配/保存 资源 + 权限集）。

聚合跨两表：`iam_resource`（本体）+ `iam_permission`（聚合内权限实体）。
get/get_all/get_by_module_and_code 装配完整聚合；create/update 整体落库。

权限是**有属性的实体**（有 id / 审计），故不能像裸映射那样差集替换、删后重建——
按 id upsert（**装配含软删行**，保证 action 身份稳定、不撞唯一约束）。
"""
from app.iam.domain.resource.entities import Permission, Resource
from app.iam.domain.resource.repositories import ResourceRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId, UserId
from app.iam.infrastructure.persistence.tortoise.postgres.models import PermissionModel, ResourceModel


def _permission_to_domain(m: PermissionModel) -> Permission:
    return Permission(
        id=PermissionId(m.id),
        resource_id=ResourceId(m.resource_id),
        action=m.action,
        name=m.name,
        description=m.description,
        status=m.status,
        permission_type=m.permission_type,
        created_at=m.created_at,
        created_by=UserId(m.created_by),
        updated_at=m.updated_at,
        updated_by=UserId(m.updated_by) if m.updated_by else None,
        deleted_at=m.deleted_at,
        deleted_by=UserId(m.deleted_by) if m.deleted_by else None,
    )


def _permission_fields(p: Permission) -> dict:
    return dict(
        id=p.id.value,
        resource_id=p.resource_id.value,
        action=p.action,
        name=p.name,
        description=p.description,
        status=p.status,
        permission_type=p.permission_type,
        created_at=p.created_at,
        created_by=p.created_by.value,
        updated_at=p.updated_at,
        updated_by=p.updated_by.value if p.updated_by else None,
        deleted_at=p.deleted_at,
        deleted_by=p.deleted_by.value if p.deleted_by else None,
    )


def to_domain(m: ResourceModel, permissions: list[Permission]) -> Resource:
    return Resource(
        id=ResourceId(m.id),
        module=m.module,
        code=m.code,
        name=m.name,
        description=m.description,
        status=m.status,
        resource_type=m.resource_type,
        permissions=permissions,
        created_at=m.created_at,
        created_by=UserId(m.created_by),
        updated_at=m.updated_at,
        updated_by=UserId(m.updated_by) if m.updated_by else None,
        deleted_at=m.deleted_at,
        deleted_by=UserId(m.deleted_by) if m.deleted_by else None,
    )


def to_model_fields(r: Resource) -> dict:
    """领域实体 → 表模型字段字典（只覆盖 `iam_resource` 的列；权限集合另行落库）。"""
    return dict(
        id=r.id.value,
        module=r.module,
        code=r.code,
        name=r.name,
        description=r.description,
        status=r.status,
        resource_type=r.resource_type,
        created_at=r.created_at,
        created_by=r.created_by.value,
        updated_at=r.updated_at,
        updated_by=r.updated_by.value if r.updated_by else None,
        deleted_at=r.deleted_at,
        deleted_by=r.deleted_by.value if r.deleted_by else None,
    )


async def _load_permissions(resource_ids: list,
                            include_deleted: bool = False) -> dict[ResourceId, list[Permission]]:
    """批量装配各资源的权限。默认只装配未删；声明/写路径显式含软删（保 action 身份）。"""
    qs = PermissionModel.filter(resource_id__in=resource_ids)
    if not include_deleted:
        qs = qs.filter(deleted_at__isnull=True)
    grouped: dict[ResourceId, list[Permission]] = {}
    for m in await qs:
        grouped.setdefault(ResourceId(m.resource_id), []).append(_permission_to_domain(m))
    return grouped


async def _upsert_permissions(resource: Resource) -> None:
    """按 id upsert 聚合内权限：已存在的行更新（**不覆盖 id**），新 action 才 create。"""
    rid = resource.id.value
    existing_ids = set(await PermissionModel.filter(resource_id=rid).values_list('id', flat=True))
    for p in resource.permissions:
        fields = _permission_fields(p)
        if p.id.value in existing_ids:
            fields.pop('id')
            await PermissionModel.filter(id=p.id.value).update(**fields)
        else:
            await PermissionModel.create(**fields)


class ResourceRepositoryTortoiseImpl(ResourceRepository):

    async def get(self, entity_id: ResourceId, *, include_deleted: bool = False,
                  include_deleted_permissions: bool = False) -> Resource | None:
        qs = ResourceModel.filter(id=entity_id.value)
        if not include_deleted:
            qs = qs.filter(deleted_at__isnull=True)
        m = await qs.first()
        if m is None:
            return None
        permissions = (await _load_permissions(
            [m.id], include_deleted_permissions)).get(ResourceId(m.id), [])
        return to_domain(m, permissions)

    async def get_by_module_and_code(self, module: str, code: str, *,
                                     include_deleted: bool = False,
                                     include_deleted_permissions: bool = False) -> Resource | None:
        qs = ResourceModel.filter(module=module, code=code)
        if not include_deleted:
            qs = qs.filter(deleted_at__isnull=True)
        m = await qs.first()
        if m is None:
            return None
        permissions = (await _load_permissions(
            [m.id], include_deleted_permissions)).get(ResourceId(m.id), [])
        return to_domain(m, permissions)

    async def get_by_permission_id(self, permission_id: PermissionId, *,
                                   include_deleted: bool = False) -> Resource | None:
        qs = PermissionModel.filter(id=permission_id.value)
        if not include_deleted:
            qs = qs.filter(deleted_at__isnull=True)
        m = await qs.first()
        if m is None:
            return None
        return await self.get(ResourceId(m.resource_id), include_deleted=include_deleted,
                              include_deleted_permissions=include_deleted)

    async def get_all(self, status: StatusEnum | None = None, deleted: bool = False,
                      include_deleted_permissions: bool = False) -> list[Resource]:
        qs = (ResourceModel.filter(deleted_at__isnull=False) if deleted
              else ResourceModel.filter(deleted_at__isnull=True))
        if status is not None:
            qs = qs.filter(status=status)
        models = await qs.order_by('module', 'code')
        if not models:
            return []
        grouped = await _load_permissions([m.id for m in models], include_deleted_permissions)
        return [to_domain(m, grouped.get(ResourceId(m.id), [])) for m in models]

    async def create(self, entity: Resource) -> Resource:
        await ResourceModel.create(**to_model_fields(entity))
        if entity.permissions:
            await PermissionModel.bulk_create(
                [PermissionModel(**_permission_fields(p)) for p in entity.permissions])
        return entity

    async def bulk_create(self, entities: list[Resource]) -> list[Resource]:
        if not entities:
            return []
        await ResourceModel.bulk_create([ResourceModel(**to_model_fields(e)) for e in entities])
        perm_rows = [PermissionModel(**_permission_fields(p)) for e in entities for p in e.permissions]
        if perm_rows:
            await PermissionModel.bulk_create(perm_rows)
        return entities

    async def update(self, entity: Resource) -> Resource:
        fields = to_model_fields(entity)
        fields.pop('id')  # 主键不参与更新
        await ResourceModel.filter(id=entity.id.value).update(**fields)
        await _upsert_permissions(entity)
        return entity

    async def hard_delete(self, entity_ids: ResourceId | list[ResourceId]) -> int:
        ids = [i.value for i in entity_ids] if isinstance(entity_ids, list) else [entity_ids.value]
        # 物理删资源连带物理删其聚合内权限（无 FK，应用层做）
        await PermissionModel.filter(resource_id__in=ids).delete()
        return await ResourceModel.filter(id__in=ids).delete()
