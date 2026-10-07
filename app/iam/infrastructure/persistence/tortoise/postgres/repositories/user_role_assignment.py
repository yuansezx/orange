"""UserRoleAssignment 的 tortoise 仓储实现（含 领域 ↔ 表 映射）。"""
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import RoleId, UserId, UserRoleId
from app.iam.domain.user_role_assignment.entities import UserRoleAssignment
from app.iam.domain.user_role_assignment.repositories import UserRoleRepository
from app.iam.infrastructure.persistence.tortoise.postgres.models import UserRoleAssignmentModel


def to_domain(m: UserRoleAssignmentModel) -> UserRoleAssignment:
    return UserRoleAssignment(
        id=UserRoleId(m.id),
        user_id=UserId(m.user_id),
        role_id=RoleId(m.role_id),
        status=m.status,
        created_at=m.created_at,
        created_by=UserId(m.created_by),
        updated_at=m.updated_at,
        updated_by=UserId(m.updated_by) if m.updated_by else None,
        deleted_at=m.deleted_at,
        deleted_by=UserId(m.deleted_by) if m.deleted_by else None,
    )


def to_model_fields(a: UserRoleAssignment) -> dict:
    """领域实体 → 表模型字段字典（必须覆盖所有列）。"""
    return dict(
        id=a.id.value,
        user_id=a.user_id.value,
        role_id=a.role_id.value,
        status=a.status,
        created_at=a.created_at,
        created_by=a.created_by.value,
        updated_at=a.updated_at,
        updated_by=a.updated_by.value if a.updated_by else None,
        deleted_at=a.deleted_at,
        deleted_by=a.deleted_by.value if a.deleted_by else None,
    )


class UserRoleRepositoryTortoiseImpl(UserRoleRepository):

    async def get(self, entity_id: UserRoleId) -> UserRoleAssignment | None:
        m = await UserRoleAssignmentModel.get_or_none(id=entity_id.value)
        return to_domain(m) if m else None

    async def create(self, entity: UserRoleAssignment) -> UserRoleAssignment:
        m = await UserRoleAssignmentModel.create(**to_model_fields(entity))
        return to_domain(m)

    async def bulk_create(self, entities: list[UserRoleAssignment]) -> list[UserRoleAssignment]:
        models = [UserRoleAssignmentModel(**to_model_fields(e)) for e in entities]
        await UserRoleAssignmentModel.bulk_create(models)
        return [to_domain(m) for m in models]

    async def update(self, entity: UserRoleAssignment) -> UserRoleAssignment:
        fields = to_model_fields(entity)
        fields.pop('id')  # 主键不参与更新
        await UserRoleAssignmentModel.filter(id=entity.id.value).update(**fields)
        return entity

    async def hard_delete(self, entity_ids: UserRoleId | list[UserRoleId]) -> int:
        ids = [i.value for i in entity_ids] if isinstance(entity_ids, list) else [entity_ids.value]
        return await UserRoleAssignmentModel.filter(id__in=ids).delete()

    async def get_by_user_id(self, user_id: UserId, include_deleted: bool = False) -> list[UserRoleAssignment]:
        qs = UserRoleAssignmentModel.filter(user_id=user_id.value)
        if not include_deleted:
            qs = qs.filter(status__not=StatusEnum.DELETED)
        models = await qs
        return [to_domain(m) for m in models]
