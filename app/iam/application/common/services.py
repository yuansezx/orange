"""应用层共用的**读侧装配服务**（跨切片复用；无状态，依赖由组合根注入）。

- `AuditService`：实体审计字段 → `AuditOut`（`created_by` 等 id → 「用户名 + 昵称」）。
- `DeptRefService`：部门 id → `DeptRefOut`（名称 + 层级路径）。
"""
from collections.abc import Mapping, Sequence

from app.core.domain.entities import AuditableEntity
from app.iam.application.common.dto import AuditOut, DeptRefOut, OperatorOut
from app.iam.domain.dept.repositories import DeptRepository
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
