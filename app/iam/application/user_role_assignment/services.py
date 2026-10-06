from datetime import datetime, UTC

from app.core.domain.units_of_work import InTransactionType
from app.iam.application.common.exceptions import PermissionDeniedException
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.role.services import RoleAccessService
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import RoleId, UserId, UserRoleId
from app.iam.domain.user_role_assignment.entities import UserRoleAssignment
from app.iam.domain.user_role_assignment.repositories import UserRoleRepository


class UserRoleApplicationService:
    """用户↔角色分配。

    关系模型为"一行/状态翻转"：一个 (用户, 角色) 只有一行。重加曾被移除的角色时，
    复活已删行而非新插（否则撞 UNIQUE(user_id, role_id)）。
    """

    def __init__(self, in_transaction: InTransactionType,
                 user_role_repo: UserRoleRepository,
                 role_access_service: RoleAccessService) -> None:
        self.in_transaction = in_transaction
        self.user_role_repo = user_role_repo
        self.role_access_service = role_access_service

    async def assign_roles_to_user(self, user_id: UserId, role_ids: list[RoleId] | set[RoleId],
                                   current_user: CurrentUser) -> None:
        """在现有基础上追加角色（幂等：已有的 ACTIVE 角色忽略）。"""
        role_ids = set(role_ids)
        async with self.in_transaction():
            if not await self.role_access_service.can_access(role_ids, current_user):
                raise PermissionDeniedException('授予的角色中存在您无权访问的角色')
            by_role = await self._existing_map(user_id)
            active = {r for r, a in by_role.items() if a.status is StatusEnum.ACTIVE}
            await self._add_roles(user_id, role_ids - active, by_role, current_user.user_id)

    async def set_user_roles(self, user_id: UserId, role_ids: list[RoleId] | set[RoleId],
                             current_user: CurrentUser) -> None:
        """把用户的角色设为恰好 role_ids（目标集即期望的 ACTIVE 集）。"""
        role_ids = set(role_ids)
        async with self.in_transaction():
            by_role = await self._existing_map(user_id)
            active = {r for r, a in by_role.items() if a.status is StatusEnum.ACTIVE}
            to_add = role_ids - active
            to_remove = active - role_ids

            # 增删都要校验访问权
            if not await self.role_access_service.can_access(to_add | to_remove, current_user):
                raise PermissionDeniedException('存在您无权访问的角色')

            # 软删除移除的（DDD：软删是业务逻辑，放实体方法，故逐行 update）
            for role_id in to_remove:
                assignment = by_role[role_id]
                assignment.delete(current_user.user_id)
                await self.user_role_repo.update(assignment)
            await self._add_roles(user_id, to_add, by_role, current_user.user_id)

    # ---------------- 内部 ----------------
    async def _existing_map(self, user_id: UserId) -> dict[RoleId, UserRoleAssignment]:
        """取该用户全部分配（含已删），按 role_id 索引。"""
        assignments = await self.user_role_repo.get_by_user_id(user_id, include_deleted=True)
        return {a.role_id: a for a in assignments}

    async def _add_roles(self, user_id: UserId, to_add: set[RoleId],
                         by_role: dict[RoleId, UserRoleAssignment], operator_id: UserId) -> None:
        """把 to_add 里的角色设为 ACTIVE：命中已有行则复活/启用，无行才新建。"""
        to_create: list[UserRoleAssignment] = []
        for role_id in to_add:
            existing = by_role.get(role_id)
            if existing is not None:
                existing.activate(operator_id)
                await self.user_role_repo.update(existing)
            else:
                to_create.append(UserRoleAssignment(
                    id=UserRoleId.new(),
                    user_id=user_id,
                    role_id=role_id,
                    status=StatusEnum.ACTIVE,
                    created_at=datetime.now(UTC),
                    created_by=operator_id,
                ))
        if to_create:
            await self.user_role_repo.bulk_create(to_create)
