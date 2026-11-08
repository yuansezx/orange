from app.core.application.dto import RequestMeta
from app.core.domain.event_bus import EventBus
from app.core.domain.units_of_work import InTransactionType
from app.core.domain.value_objects import EventId
from app.core.utils.schemas import PageResult
from app.iam.application.common.decorators import requires_permission
from app.iam.application.common.exceptions import PermissionDeniedException
from app.iam.application.common.ports import AuditLogWriterPort
from app.iam.application.role.exceptions import RoleNotFoundException
from app.iam.application.user.dto import UserRefOut
from app.iam.application.user.exceptions import UserNotExistException
from app.iam.application.user_role_assignment.dto import GetRoleCandidatesIn, RoleCandidateUserOut
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.role.repositories import RoleRepository
from app.iam.domain.role.services import RoleAccessService
from app.iam.domain.shared.value_objects import RoleId, UserId
from app.iam.domain.user.repositories import SearchUser, UserRepository
from app.iam.domain.user.services import UserAccessService
from app.iam.domain.user_role_assignment.events import UserRolesChanged
from app.iam.domain.user_role_assignment.repositories import UserRoleRepository
from app.iam.domain.user_role_assignment.services import UserRoleAssignmentService


class UserRoleApplicationService:
    """用户↔角色关系管理（增量）。

    - 用户视角：管理某个用户的角色；
    - 角色视角：管理某个角色的成员。
    两者语义都是「只改本次 add/remove 指定的关系」，未提及的分配保持原样。
    """

    def __init__(self, in_transaction: InTransactionType,
                 user_repo: UserRepository,
                 role_repo: RoleRepository,
                 user_role_repo: UserRoleRepository,
                 role_access_service: RoleAccessService,
                 user_access_service: UserAccessService,
                 user_role_assignment_service: UserRoleAssignmentService,
                 audit_log_writer: AuditLogWriterPort,
                 event_bus: EventBus) -> None:
        self.in_transaction = in_transaction
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.user_role_repo = user_role_repo
        self.role_access_service = role_access_service
        self.user_access_service = user_access_service
        self.user_role_assignment_service = user_role_assignment_service
        self.audit_log_writer = audit_log_writer
        self.event_bus = event_bus

    @requires_permission('iam:user_role:assign')
    async def patch_user_roles(self, user_id: UserId, add_role_ids: list[RoleId],
                               remove_role_ids: list[RoleId], current_user: CurrentUser,
                               request_meta: RequestMeta | None = None) -> None:
        async with self.in_transaction():
            user = await self.user_repo.get(user_id)
            if user is None:
                raise UserNotExistException('用户不存在')
            if not await self.user_access_service.can_access(user_id, current_user):
                raise PermissionDeniedException('无权访问该用户')

            changed_roles = set(add_role_ids) | set(remove_role_ids)
            if changed_roles:
                roles = await self.role_repo.get_by_ids(list(changed_roles))
                if len(roles) != len(changed_roles):
                    raise RoleNotFoundException('存在不存在的角色')
                if not await self.role_access_service.can_access(changed_roles, current_user):
                    raise PermissionDeniedException('存在您无权访问的角色')

            added, removed = await self.user_role_assignment_service.apply_user_role_delta(
                user_id, add_role_ids, remove_role_ids, current_user.user_id)
            if added or removed:
                await self.audit_log_writer.write(
                    current_user=current_user,
                    request_meta=request_meta,
                    resource='user_role',
                    action='assign',
                    summary=f'管理用户 {user.username} 的角色',
                    target_type='user',
                    target_id=str(user_id.value),
                    target_name=user.username,
                    detail={
                        'added_role_ids': sorted(str(r.value) for r in added),
                        'removed_role_ids': sorted(str(r.value) for r in removed),
                    },
                )

        if added or removed:
            await self.event_bus.publish(UserRolesChanged(id=EventId.new(), user_id=user_id))

    @requires_permission('iam:user_role:assign')
    async def patch_role_users(self, role_id: RoleId, add_user_ids: list[UserId],
                               remove_user_ids: list[UserId], current_user: CurrentUser,
                               request_meta: RequestMeta | None = None) -> None:
        async with self.in_transaction():
            role = await self.role_repo.get(role_id)
            if role is None:
                raise RoleNotFoundException('角色不存在')
            if not await self.role_access_service.can_access(role_id, current_user):
                raise PermissionDeniedException('无权访问该角色')

            changed_users = set(add_user_ids) | set(remove_user_ids)
            if changed_users:
                users = await self.user_repo.get_by_ids(list(changed_users))
                if len(users) != len(changed_users):
                    raise UserNotExistException('存在不存在的用户')
                if not await self.user_access_service.can_access(changed_users, current_user):
                    raise PermissionDeniedException('存在您无权访问的用户')

            added, removed = await self.user_role_assignment_service.apply_role_user_delta(
                role_id, add_user_ids, remove_user_ids, current_user.user_id)
            if added or removed:
                await self.audit_log_writer.write(
                    current_user=current_user,
                    request_meta=request_meta,
                    resource='user_role',
                    action='assign',
                    summary=f'管理角色 {role.name} 的成员',
                    target_type='role',
                    target_id=str(role_id.value),
                    target_name=role.name,
                    detail={
                        'added_user_ids': sorted(str(u.value) for u in added),
                        'removed_user_ids': sorted(str(u.value) for u in removed),
                    },
                )

        for affected_user_id in sorted(added | removed, key=str):
            await self.event_bus.publish(
                UserRolesChanged(id=EventId.new(), user_id=affected_user_id))

    @requires_permission(('iam:user_role:assign', 'iam:user:read'))
    async def get_role_users(self, role_id: RoleId, current_user: CurrentUser) -> list[UserRefOut]:
        """角色当前可管理成员（ACTIVE 分配 ∩ 当前用户数据范围）。"""
        role = await self.role_repo.get(role_id)
        if role is None:
            raise RoleNotFoundException('角色不存在')
        if not await self.role_access_service.can_access(role_id, current_user):
            raise PermissionDeniedException('无权访问该角色')

        user_ids = await self.user_role_repo.get_user_ids_by_role(role_id)
        if not user_ids:
            return []
        allowed = await self.user_repo.get_allowed_user_ids(current_user)
        manageable = [uid for uid in user_ids if uid in allowed]
        if not manageable:
            return []

        users = await self.user_repo.get_by_ids(manageable)
        by_id = {u.id: u for u in users}
        return sorted(
            (UserRefOut(id=uid, username=by_id[uid].username, nickname=by_id[uid].nickname)
             for uid in manageable if uid in by_id),
            key=lambda u: u.username,
        )

    @requires_permission(('iam:user_role:assign', 'iam:user:read'))
    async def get_role_candidates(self, role_id: RoleId, data: GetRoleCandidatesIn,
                                  current_user: CurrentUser) -> PageResult[RoleCandidateUserOut]:
        """分页候选用户 + 每行 selected 标记（数据范围在用户检索侧过滤）。"""
        role = await self.role_repo.get(role_id)
        if role is None:
            raise RoleNotFoundException('角色不存在')
        if not await self.role_access_service.can_access(role_id, current_user):
            raise PermissionDeniedException('无权访问该角色')

        page = await self.user_repo.search(
            SearchUser(keyword=data.keyword, status=data.status, user_type=data.user_type),
            page_size=data.page_size,
            page=data.page,
            scope=current_user.data_scope_spec,
        )
        users = page.data or []
        assigned = await self.user_role_repo.get_assigned_user_ids(
            role_id, [u.id for u in users])

        return PageResult[RoleCandidateUserOut](
            page=page.page,
            page_size=page.page_size,
            total=page.total,
            data=[
                RoleCandidateUserOut(
                    id=u.id,
                    username=u.username,
                    nickname=u.nickname or u.username,
                    user_type=u.user_type,
                    status=u.status,
                    selected=u.id in assigned,
                )
                for u in users
            ],
        )
