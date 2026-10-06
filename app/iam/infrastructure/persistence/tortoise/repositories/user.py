"""User 聚合的 tortoise 仓储实现（含 领域 User ↔ UserModel 的映射）。

映射归仓储负责（DDD：仓储处理实体与表模型的转换）。
"""
from app.core.utils.schemas import PageResult
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import Email, Phone, UserId, DeptId
from app.iam.domain.user.entities import User
from app.iam.domain.user.enums import UserTypeEnum
from app.iam.domain.user.repositories import SearchUser, UserRepository
from app.iam.infrastructure.persistence.tortoise.models import UserModel


def to_domain(m: UserModel) -> User:
    return User(
        id=UserId(m.id),
        username=m.username,
        nickname=m.nickname,
        password_hash=m.password_hash,
        email=Email(m.email) if m.email else None,
        phone=Phone(m.phone) if m.phone else None,
        user_type=m.user_type,
        status=m.status,
        need_change_password=m.need_change_password,
        password_updated_at=m.password_updated_at,
        description=m.description,
        dept_id=DeptId(m.dept_id) if m.dept_id else None,
        created_at=m.created_at,
        created_by=UserId(m.created_by),
        updated_at=m.updated_at,
        updated_by=UserId(m.updated_by) if m.updated_by else None,
        deleted_at=m.deleted_at,
        deleted_by=UserId(m.deleted_by) if m.deleted_by else None,
    )


def to_model_fields(u: User) -> dict:
    """领域实体 → 表模型字段字典（必须覆盖所有列）。"""
    return dict(
        id=u.id.value,
        username=u.username,
        nickname=u.nickname,
        password_hash=u.password_hash,
        email=u.email.value if u.email else None,
        phone=u.phone.value if u.phone else None,
        user_type=u.user_type,
        status=u.status,
        need_change_password=u.need_change_password,
        password_updated_at=u.password_updated_at,
        description=u.description,
        dept_id=u.dept_id.value if u.dept_id else None,
        created_at=u.created_at,
        created_by=u.created_by.value,
        updated_at=u.updated_at,
        updated_by=u.updated_by.value if u.updated_by else None,
        deleted_at=u.deleted_at,
        deleted_by=u.deleted_by.value if u.deleted_by else None,
    )


class UserRepositoryTortoiseImpl(UserRepository):

    async def get(self, entity_id: UserId) -> User | None:
        m = await UserModel.get_or_none(id=entity_id.value)
        return to_domain(m) if m else None

    async def create(self, entity: User) -> User:
        m = await UserModel.create(**to_model_fields(entity))
        return to_domain(m)

    async def bulk_create(self, entities: list[User]) -> list[User]:
        models = [UserModel(**to_model_fields(e)) for e in entities]
        await UserModel.bulk_create(models)
        return [to_domain(m) for m in models]

    async def update(self, entity: User) -> User:
        fields = to_model_fields(entity)
        fields.pop('id')  # 主键不参与更新
        await UserModel.filter(id=entity.id.value).update(**fields)
        return entity

    async def hard_delete(self, entity_ids: UserId | list[UserId]) -> int:
        ids = [i.value for i in entity_ids] if isinstance(entity_ids, list) else [entity_ids.value]
        # 物理删除（tortoise QuerySet.delete 即为物理删）
        return await UserModel.filter(id__in=ids).delete()

    async def get_by_username(self, username: str) -> User | None:
        m = await UserModel.get_or_none(username=username)
        return to_domain(m) if m else None

    async def get_id_by_username(self, username: str) -> UserId | None:
        ids = await UserModel.filter(username=username).values_list('id', flat=True)
        return UserId(ids[0]) if ids else None

    async def get_id_by_phone(self, phone: Phone) -> UserId | None:
        ids = await UserModel.filter(phone=phone.value).values_list('id', flat=True)
        return UserId(ids[0]) if ids else None

    async def get_id_by_email(self, email: Email) -> UserId | None:
        ids = await UserModel.filter(email=email.value).values_list('id', flat=True)
        return UserId(ids[0]) if ids else None

    async def exists_by_user_type(self, user_type: UserTypeEnum) -> bool:
        return await UserModel.filter(user_type=user_type).exists()

    async def get_allowed_user_ids(self, current_user: CurrentUser) -> set[UserId]:
        # TODO: 数据权限——依赖 role / dept / user_role 等表，待那些模型落地后实现
        raise NotImplementedError('数据权限查询待角色/部门表落地后实现')

    async def search(self, search_by: SearchUser, page_size: int, page: int,
                     current_user: CurrentUser) -> PageResult[User]:
        # TODO: 动态过滤 + 数据权限 + 分页
        raise NotImplementedError('用户检索待实现')
