from datetime import datetime, UTC

from app.iam.application.common.exceptions import PermissionDeniedException
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.enums import Status
from app.iam.domain.role.services import RoleAccessService
from app.iam.domain.shared.units_of_work import InTransactionType
from app.iam.domain.shared.value_objects import UserId, RoleId
from app.iam.domain.user_role_assignment.entities import UserRoleAssignment
from app.iam.domain.user_role_assignment.ports import UserRoleIdProvider
from app.iam.domain.user_role_assignment.repositories import UserRoleRepository


class UserRoleApplicationService:
    def __init__(self, in_transaction: InTransactionType, user_role_repo: UserRoleRepository,
                 role_access_service: RoleAccessService,
                 id_provider: UserRoleIdProvider) -> None:
        self.in_transaction = in_transaction
        self.user_role_repo = user_role_repo

        self.role_access_service = role_access_service

        self.id_provider = id_provider

    async def assign_roles_to_user(self, user_id: UserId, role_ids: list[RoleId] | set[RoleId], current_user:CurrentUser) -> None:
        if not await self.role_access_service.can_access(role_ids, current_user):
            raise PermissionDeniedException('授予的角色中存在您无权访问的角色')
        await self._assign_roles_to_user(user_id, role_ids, current_user.user_id)

    async def set_user_roles(self, user_id: UserId, role_ids: list[RoleId] | set[RoleId], current_user:CurrentUser) -> None:
        if not isinstance(role_ids, set):
            role_ids = set(role_ids)
        current_assignments = await self.user_role_repo.get_by_user_id(user_id)
        assignment_map = {assignment.role_id : assignment for assignment in current_assignments}
        current_role_ids = set(assignment_map.keys())

        to_add = role_ids - current_role_ids
        to_remove = current_role_ids - role_ids

        # 权限校验，删除和增加都要校验
        if not await self.role_access_service.can_access(to_add | to_remove, current_user):
            raise PermissionDeniedException('存在您无权访问的角色')

        # 如果有嵌套事务，让异常穿透所有事务即可完全回滚，如果要保存点回滚，则在主事务中要捕获子事务的异常
        async with self.in_transaction():
            # ddd架构下，软删除包含业务逻辑，放在了实体内部，也导致无法使用orm/数据库的批量更新，需要注意性能问题
            for role_id in to_remove:
                assignment = assignment_map[role_id]
                assignment.delete(current_user.user_id)
                await self.user_role_repo.update(assignment)
            # 调内部方法，不重复检验
            await self._assign_roles_to_user(user_id, to_add, current_user.user_id)

    """---内部方法---"""
    async def _assign_roles_to_user(self, user_id: UserId, role_ids: list[RoleId] | set[RoleId], operator_id: UserId) -> None:
        user_role_assignments = [UserRoleAssignment(id=self.id_provider.generate(),
                                                    user_id=user_id,
                                                    role_id=role_id,
                                                    status=Status.ACTIVE,
                                                    created_at=datetime.now(UTC),
                                                    created_by=operator_id) for role_id in role_ids]

        await self.user_role_repo.bulk_create(user_role_assignments)



