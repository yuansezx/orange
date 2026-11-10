"""ApiKey 的 tortoise 仓储实现（含 领域 ↔ 表 映射）。"""
from datetime import datetime

from app.iam.domain.api_key.entities import ApiKey
from app.iam.domain.api_key.repositories import ApiKeyRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import ApiKeyId, DeptId, UserId
from app.iam.infrastructure.persistence.tortoise.postgres.models import ApiKeyModel


def to_domain(m: ApiKeyModel) -> ApiKey:
    return ApiKey(
        id=ApiKeyId(m.id),
        user_id=UserId(m.user_id),
        name=m.name,
        token_hash=m.token_hash,
        token_masked=m.token_masked,
        scopes=frozenset(m.scopes or ()),
        data_scope_kind=m.data_scope_kind,
        data_scope_dept_ids=frozenset(DeptId(d) for d in (m.data_scope_dept_ids or ())),
        status=m.status,
        expires_at=m.expires_at,
        last_used_at=m.last_used_at,
        created_at=m.created_at,
        created_by=UserId(m.created_by),
        updated_at=m.updated_at,
        updated_by=UserId(m.updated_by) if m.updated_by else None,
        deleted_at=m.deleted_at,
        deleted_by=UserId(m.deleted_by) if m.deleted_by else None,
    )


def to_model_fields(k: ApiKey) -> dict:
    """领域实体 → 表模型字段字典（必须覆盖所有列）。"""
    return dict(
        id=k.id.value,
        user_id=k.user_id.value,
        name=k.name,
        token_hash=k.token_hash,
        token_masked=k.token_masked,
        scopes=sorted(k.scopes),
        data_scope_kind=k.data_scope_kind,
        data_scope_dept_ids=[d.value for d in k.data_scope_dept_ids],
        status=k.status,
        expires_at=k.expires_at,
        last_used_at=k.last_used_at,
        created_at=k.created_at,
        created_by=k.created_by.value,
        updated_at=k.updated_at,
        updated_by=k.updated_by.value if k.updated_by else None,
        deleted_at=k.deleted_at,
        deleted_by=k.deleted_by.value if k.deleted_by else None,
    )


class ApiKeyRepositoryTortoiseImpl(ApiKeyRepository):

    async def get(self, entity_id: ApiKeyId, *,
                  include_deleted: bool = False) -> ApiKey | None:
        qs = ApiKeyModel.filter(id=entity_id.value)
        if not include_deleted:
            qs = qs.filter(deleted_at__isnull=True)
        m = await qs.first()
        return to_domain(m) if m else None

    async def create(self, entity: ApiKey) -> ApiKey:
        m = await ApiKeyModel.create(**to_model_fields(entity))
        return to_domain(m)

    async def bulk_create(self, entities: list[ApiKey]) -> list[ApiKey]:
        models = [ApiKeyModel(**to_model_fields(e)) for e in entities]
        await ApiKeyModel.bulk_create(models)
        return [to_domain(m) for m in models]

    async def update(self, entity: ApiKey) -> ApiKey:
        fields = to_model_fields(entity)
        fields.pop('id')  # 主键不参与更新
        await ApiKeyModel.filter(id=entity.id.value).update(**fields)
        return entity

    async def hard_delete(self, entity_ids: ApiKeyId | list[ApiKeyId]) -> int:
        ids = [i.value for i in entity_ids] if isinstance(entity_ids, list) else [entity_ids.value]
        return await ApiKeyModel.filter(id__in=ids).delete()

    async def get_by_token_hash(self, token_hash: str, *,
                                include_deleted: bool = False) -> ApiKey | None:
        qs = ApiKeyModel.filter(token_hash=token_hash)
        if not include_deleted:
            qs = qs.filter(deleted_at__isnull=True)
        m = await qs.first()
        return to_domain(m) if m else None

    async def get_all(self, user_id: UserId | None = None, status: StatusEnum | None = None,
                      deleted: bool = False) -> list[ApiKey]:
        qs = ApiKeyModel.filter(deleted_at__isnull=not deleted)
        if user_id is not None:
            qs = qs.filter(user_id=user_id.value)
        if status is not None:
            qs = qs.filter(status=status)
        models = await qs.order_by('-created_at')
        return [to_domain(m) for m in models]

    async def update_last_used(self, api_key_id: ApiKeyId, used_at: datetime) -> None:
        await ApiKeyModel.filter(id=api_key_id.value).update(last_used_at=used_at)

    async def hard_delete_by_user(self, user_id: UserId) -> int:
        return await ApiKeyModel.filter(user_id=user_id.value).delete()
