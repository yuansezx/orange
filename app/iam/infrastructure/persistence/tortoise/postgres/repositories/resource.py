"""Resource 目录的 tortoise 仓储实现（含 领域 Resource ↔ ResourceModel 的映射）。"""
from app.iam.domain.resource.entities import Resource
from app.iam.domain.resource.repositories import ResourceRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import ResourceId, UserId
from app.iam.infrastructure.persistence.tortoise.postgres.models import ResourceModel


def to_domain(m: ResourceModel) -> Resource:
    return Resource(
        id=ResourceId(m.id),
        module=m.module,
        code=m.code,
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


def to_model_fields(r: Resource) -> dict:
    """领域实体 → 表模型字段字典（必须覆盖所有列）。"""
    return dict(
        id=r.id.value,
        module=r.module,
        code=r.code,
        name=r.name,
        description=r.description,
        status=r.status,
        created_at=r.created_at,
        created_by=r.created_by.value,
        updated_at=r.updated_at,
        updated_by=r.updated_by.value if r.updated_by else None,
        deleted_at=r.deleted_at,
        deleted_by=r.deleted_by.value if r.deleted_by else None,
    )


class ResourceRepositoryTortoiseImpl(ResourceRepository):

    async def get(self, entity_id: ResourceId) -> Resource | None:
        m = await ResourceModel.get_or_none(id=entity_id.value)
        return to_domain(m) if m else None

    async def create(self, entity: Resource) -> Resource:
        m = await ResourceModel.create(**to_model_fields(entity))
        return to_domain(m)

    async def bulk_create(self, entities: list[Resource]) -> list[Resource]:
        models = [ResourceModel(**to_model_fields(e)) for e in entities]
        await ResourceModel.bulk_create(models)
        return [to_domain(m) for m in models]

    async def update(self, entity: Resource) -> Resource:
        fields = to_model_fields(entity)
        fields.pop('id')  # 主键不参与更新
        await ResourceModel.filter(id=entity.id.value).update(**fields)
        return entity

    async def hard_delete(self, entity_ids: ResourceId | list[ResourceId]) -> int:
        ids = [i.value for i in entity_ids] if isinstance(entity_ids, list) else [entity_ids.value]
        return await ResourceModel.filter(id__in=ids).delete()

    async def get_by_module_and_code(self, module: str, code: str) -> Resource | None:
        m = await ResourceModel.get_or_none(module=module, code=code)
        return to_domain(m) if m else None

    async def get_all(self) -> list[Resource]:
        models = await ResourceModel.filter(status__not=StatusEnum.DELETED).order_by('module', 'code')
        return [to_domain(m) for m in models]
