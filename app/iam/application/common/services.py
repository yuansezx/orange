"""应用层共用的服务（跨切片复用；无状态，依赖由组合根注入）。

- `AuditService`：实体审计字段 → `AuditOut`（`created_by` 等 id → 「用户名 + 昵称」）。
- `DeptRefService`：部门 id → `DeptRefOut`（名称 + 层级路径）。
- `CurrentUserSnapshotService`：按 user 读取/构建 `CurrentUser` 快照（缓存优先，缺失回填）。
"""
from collections.abc import Mapping, Sequence

from app.core.domain.entities import AuditableEntity
from app.iam.application.common.dto import AuditOut, DeptRefOut, OperatorOut
from app.iam.application.common.exceptions import InvalidTokenException
from app.iam.application.common.queries import EffectivePermissionQuery
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.current_user.repositories import CurrentUserRepository
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.services import DataScopeService
from app.iam.domain.shared.value_objects import DeptId, UserId
from app.iam.domain.user.entities import User
from app.iam.domain.user.repositories import UserRepository


def _operator(users: Mapping[UserId, User], uid: UserId | None) -> OperatorOut | None:
    """操作人 id 直接来自实体审计列；用户行不存在（已硬删）→ 名字为空。"""
    if uid is None:
        return None
    user = users.get(uid)
    return OperatorOut(
        id=uid,
        username=user.username if user else None,
        nickname=user.nickname if user else None,
    )


class AuditService:
    """装配实体的审计信息（平铺）——人从 id 解析成「用户名 + 昵称」。"""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def build(self, entity: AuditableEntity) -> AuditOut:
        return (await self.build_many([entity]))[0]

    async def build_many(self, entities: Sequence[AuditableEntity]) -> list[AuditOut]:
        """批量装配（列表用）——操作人 id 取并集后一次查询，避免 N+1。"""
        ids: dict[UserId, None] = {}
        for entity in entities:
            for uid in (entity.created_by, entity.updated_by, entity.deleted_by):
                if uid is not None:
                    ids[uid] = None
        # 审计要能解析已删操作人（如 deleted_by），故显式含已删
        users = {u.id: u for u in await self.user_repo.get_by_ids(
            list(ids), include_deleted=True)} if ids else {}
        return [self._assemble(entity, users) for entity in entities]

    @staticmethod
    def _assemble(entity: AuditableEntity, users: Mapping[UserId, User]) -> AuditOut:
        return AuditOut(
            created_by=_operator(users, entity.created_by),
            updated_by=_operator(users, entity.updated_by),
            deleted_by=_operator(users, entity.deleted_by),
        )


class DeptRefService:
    """装配部门引用——名称 + 层级路径（路径由物化路径 `ancestors` 拼出，无 N+1）。"""

    def __init__(self, dept_repo: DeptRepository) -> None:
        self.dept_repo = dept_repo

    async def build(self, dept_ids: Sequence[DeptId]) -> list[DeptRefOut]:
        if not dept_ids:
            return []

        targets = await self.dept_repo.get_by_ids(list(dept_ids))

        needed: dict[DeptId, None] = {}
        for dept in targets:
            needed[dept.id] = None
            for ancestor in dept.ancestors:
                needed[ancestor] = None
        names = {d.id: d.name for d in await self.dept_repo.get_by_ids(list(needed))}

        refs = [
            DeptRefOut(
                id=dept.id,
                name=dept.name,
                path=' / '.join([*(names[a] for a in dept.ancestors if a in names), dept.name]),
            )
            for dept in targets
        ]
        refs.sort(key=lambda ref: ref.path)
        return refs


class CurrentUserSnapshotService:
    """按 user_id 读取/构建 `CurrentUser` 快照（缓存优先，缺失回填）。

    跨切片共享：登录/会话认证与 API Key 认证都通过它取同一份快照，
    避免 application service 之间互相依赖。
    """

    def __init__(self, *, user_repo: UserRepository,
                 current_user_repo: CurrentUserRepository,
                 effective_permission_query: EffectivePermissionQuery,
                 data_scope_service: DataScopeService) -> None:
        self.user_repo = user_repo
        self.current_user_repo = current_user_repo
        self.effective_permission_query = effective_permission_query
        self.data_scope_service = data_scope_service

    async def get_by_id(self, user_id: UserId) -> CurrentUser:
        current_user = await self.current_user_repo.get(user_id)
        if current_user is not None:
            return current_user
        # 快照缺失（过期/被清）→ 重解析并回填，不要求重登
        user = await self.user_repo.get(user_id)  # 仓储默认不返回已删
        if user is None or user.status is not StatusEnum.ACTIVE:
            raise InvalidTokenException('用户不可用')
        current_user = await self.build(user)
        await self.current_user_repo.set(current_user)
        return current_user

    async def build(self, user: User) -> CurrentUser:
        effective = await self.effective_permission_query.resolve(user.id)
        data_scope_spec = await self.data_scope_service.resolve(user)
        return CurrentUser(
            user_id=user.id,
            username=user.username,
            nickname=user.nickname,
            user_type=user.user_type,
            roles=sorted(effective.roles, key=lambda r: r.code),
            dept_id=user.dept_id,
            avatar_key=user.avatar_key,
            permission_codes=sorted(effective.permission_codes),
            data_scope_spec=data_scope_spec,
        )
