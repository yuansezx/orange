"""Dept 聚合的 tortoise 仓储实现（含 领域 Dept ↔ DeptModel 的映射）。"""
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.dept.entities import Dept
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum
from app.iam.domain.shared.value_objects import Email, Phone, DeptId, UserId
from app.iam.infrastructure.persistence.tortoise.postgres.models import DeptModel


def to_domain(m: DeptModel) -> Dept:
    return Dept(
        id=DeptId(m.id),
        name=m.name,
        parent_id=DeptId(m.parent_id) if m.parent_id else None,
        ancestors=[DeptId(a) for a in (m.ancestors or [])],
        leader_id=UserId(m.leader_id) if m.leader_id else None,
        email=Email(m.email) if m.email else None,
        phone=Phone(m.phone) if m.phone else None,
        status=m.status,
        description=m.description,
        created_at=m.created_at,
        created_by=UserId(m.created_by),
        updated_at=m.updated_at,
        updated_by=UserId(m.updated_by) if m.updated_by else None,
        deleted_at=m.deleted_at,
        deleted_by=UserId(m.deleted_by) if m.deleted_by else None,
    )


def to_model_fields(d: Dept) -> dict:
    """领域实体 → 表模型字段字典（必须覆盖所有列）。"""
    return dict(
        id=d.id.value,
        name=d.name,
        parent_id=d.parent_id.value if d.parent_id else None,
        ancestors=[a.value for a in d.ancestors],
        leader_id=d.leader_id.value if d.leader_id else None,
        email=d.email.value if d.email else None,
        phone=d.phone.value if d.phone else None,
        status=d.status,
        description=d.description,
        created_at=d.created_at,
        created_by=d.created_by.value,
        updated_at=d.updated_at,
        updated_by=d.updated_by.value if d.updated_by else None,
        deleted_at=d.deleted_at,
        deleted_by=d.deleted_by.value if d.deleted_by else None,
    )


class DeptRepositoryTortoiseImpl(DeptRepository):

    async def get(self, entity_id: DeptId) -> Dept | None:
        m = await DeptModel.get_or_none(id=entity_id.value)
        return to_domain(m) if m else None

    async def create(self, entity: Dept) -> Dept:
        m = await DeptModel.create(**to_model_fields(entity))
        return to_domain(m)

    async def bulk_create(self, entities: list[Dept]) -> list[Dept]:
        models = [DeptModel(**to_model_fields(e)) for e in entities]
        await DeptModel.bulk_create(models)
        return [to_domain(m) for m in models]

    async def update(self, entity: Dept) -> Dept:
        fields = to_model_fields(entity)
        fields.pop('id')  # 主键不参与更新
        await DeptModel.filter(id=entity.id.value).update(**fields)
        return entity

    async def hard_delete(self, entity_ids: DeptId | list[DeptId]) -> int:
        ids = [i.value for i in entity_ids] if isinstance(entity_ids, list) else [entity_ids.value]
        # 物理删除（tortoise QuerySet.delete 即为物理删）
        return await DeptModel.filter(id__in=ids).delete()

    async def get_all(self, status: StatusEnum | None = None) -> list[Dept]:
        qs = (DeptModel.filter(status=status) if status is not None
              else DeptModel.exclude(status=StatusEnum.DELETED))
        models = await qs.order_by('name')
        return [to_domain(m) for m in models]

    async def get_descendants(self, dept_id: DeptId) -> list[Dept]:
        # ancestors @> [dept_id]（走 GIN 索引）；软删的子孙不参与移动重写
        models = await DeptModel.filter(
            ancestors__contains=[dept_id.value], status__not=StatusEnum.DELETED)
        return [to_domain(m) for m in models]

    async def has_children(self, dept_id: DeptId) -> bool:
        return await DeptModel.filter(
            parent_id=dept_id.value, status__not=StatusEnum.DELETED).exists()

    async def get_by_parent_and_name(self, parent_id: DeptId | None, name: str) -> Dept | None:
        m = await DeptModel.get_or_none(
            parent_id=parent_id.value if parent_id else None,
            name=name,
            status__not=StatusEnum.DELETED,
        )
        return to_domain(m) if m else None

    async def get_by_ids(self, dept_ids: list[DeptId]) -> list[Dept]:
        ids = [d.value for d in dept_ids]
        models = await DeptModel.filter(id__in=ids, status__not=StatusEnum.DELETED)
        return [to_domain(m) for m in models]

    async def get_allowed_dept_ids(self, current_user: CurrentUser) -> set[DeptId]:
        spec = current_user.data_scope_spec
        if spec.kind is DataScopeEnum.ALL:
            ids = await DeptModel.filter(status__not=StatusEnum.DELETED).values_list('id', flat=True)
            return {DeptId(i) for i in ids}
        return set(spec.dept_ids)
