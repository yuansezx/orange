"""Permission 目录的 tortoise 仓储实现（含 领域 Permission ↔ PermissionModel 的映射）。"""
from app.iam.domain.permission.entities import Permission
from app.iam.domain.permission.repositories import PermissionRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId, UserId
from app.iam.infrastructure.persistence.tortoise.models import PermissionModel


def to_domain(m: PermissionModel) -> Permission:
    return Permission(
        id=PermissionId(m.id),
        resource_id=ResourceId(m.resource_id),
        action=m.action,
        name=m.name,
        description=m.description,
        status=m.status,
        created_at=m.created_at,
        created_by=UserId(m.created_by),
        updated_at=m.updated_at,
        updated_by=UserId(m.updated_by) if m.updated_by else None,
        deleted_at=m.deleted_at,
        deleted_by=UserId(m.deleted_by) if m.deleted_by else None,
    )


def to_model_fields(p: Permission) -> dict:
    """领域实体 → 表模型字段字典（必须覆盖所有列）。"""
    return dict(
        id=p.id.value,
        resource_id=p.resource_id.value,
        action=p.action,
        name=p.name,
        description=p.description,
        status=p.status,
        created_at=p.created_at,
        created_by=p.created_by.value,
        updated_at=p.updated_at,
        updated_by=p.updated_by.value if p.updated_by else None,
        deleted_at=p.deleted_at,
        deleted_by=p.deleted_by.value if p.deleted_by else None,
    )


class PermissionRepositoryTortoiseImpl(PermissionRepository):

    async def get(self, entity_id: PermissionId) -> Permission | None:
        m = await PermissionModel.get_or_none(id=entity_id.value)
        return to_domain(m) if m else None

    async def create(self, entity: Permission) -> Permission:
        m = await PermissionModel.create(**to_model_fields(entity))
        return to_domain(m)

    async def bulk_create(self, entities: list[Permission]) -> list[Permission]:
        models = [PermissionModel(**to_model_fields(e)) for e in entities]
        await PermissionModel.bulk_create(models)
        return [to_domain(m) for m in models]

    async def update(self, entity: Permission) -> Permission:
        fields = to_model_fields(entity)
        fields.pop('id')  # 主键不参与更新
        await PermissionModel.filter(id=entity.id.value).update(**fields)
        return entity

    async def hard_delete(self, entity_ids: PermissionId | list[PermissionId]) -> int:
        ids = [i.value for i in entity_ids] if isinstance(entity_ids, list) else [entity_ids.value]
        return await PermissionModel.filter(id__in=ids).delete()

    async def get_by_resource_and_action(self, resource_id: ResourceId, action: str) -> Permission | None:
        m = await PermissionModel.get_or_none(resource_id=resource_id.value, action=action)
        return to_domain(m) if m else None

    async def get_by_resource_ids(self, resource_ids: list[ResourceId]) -> list[Permission]:
        ids = [r.value for r in resource_ids]
        models = await PermissionModel.filter(resource_id__in=ids, status__not=StatusEnum.DELETED)
        return [to_domain(m) for m in models]

    async def get_by_ids(self, permission_ids: list[PermissionId]) -> list[Permission]:
        ids = [p.value for p in permission_ids]
        models = await PermissionModel.filter(id__in=ids, status__not=StatusEnum.DELETED)
        return [to_domain(m) for m in models]
