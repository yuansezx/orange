from datetime import datetime, UTC

from app.core.domain.event_bus import EventBus
from app.core.domain.units_of_work import InTransactionType
from app.core.domain.value_objects import EventId
from app.iam.application.common.decorators import requires_permission
from app.iam.application.common.exceptions import PermissionDeniedException
from app.iam.application.dept.exceptions import DeptNotFoundException
from app.iam.application.resource.exceptions import PermissionNotFoundException
from app.iam.application.role.dto import (
    CreateRoleIn,
    RoleDetailOut,
    RoleOut,
    UpdateRoleIn,
)
from app.iam.application.role.exceptions import RoleCodeConflictException, RoleNotFoundException
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.permission.repositories import PermissionRepository
from app.iam.domain.role.entities import Role
from app.iam.domain.role.events import RoleChanged
from app.iam.domain.role.repositories import RoleRepository
from app.iam.domain.role.services import RoleAccessService
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, PermissionId, RoleId


class RoleApplicationService:
    """角色用例：CRUD + 角色↔权限 / 角色↔部门 的整体设置。

    Role 是聚合根（持有权限/部门集合），故一律 load → 实体方法变更 → update。
    """

    def __init__(self, in_transaction: InTransactionType,
                 role_repo: RoleRepository,
                 permission_repo: PermissionRepository,
                 dept_repo: DeptRepository,
                 role_access_service: RoleAccessService,
                 event_bus: EventBus) -> None:
        self.in_transaction = in_transaction
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.dept_repo = dept_repo
        self.role_access_service = role_access_service
        self.event_bus = event_bus

    # ---------------- 写 ----------------
    @requires_permission('iam:role:create')
    async def create_role(self, data: CreateRoleIn, current_user: CurrentUser) -> Role:
        async with self.in_transaction():
            if await self.role_repo.get_by_code(data.code):
                raise RoleCodeConflictException(f'角色 code 已存在：{data.code}')
            permission_ids = set(data.permission_ids)
            dept_ids = set(data.dept_ids)
            if permission_ids:
                await self._ensure_permissions_exist(permission_ids)
            if dept_ids:
                await self._ensure_depts_exist(dept_ids)
            return await self.role_repo.create(Role(
                id=RoleId.new(),
                code=data.code,
                name=data.name,
                data_scope=data.data_scope,
                status=StatusEnum.ACTIVE,
                description=data.description,
                permission_ids=permission_ids,
                custom_dept_ids=dept_ids,
                created_at=datetime.now(UTC),
                created_by=current_user.user_id,
            ))

    @requires_permission('iam:role:update')
    async def update_role(self, data: UpdateRoleIn, current_user: CurrentUser) -> None:
        """整体替换角色（PUT 语义）：属性 / 权限集 / 数据范围部门集一次提交，单事务原子。"""
        async with self.in_transaction():
            role = await self._load_accessible(data.id, current_user)
            permission_ids = set(data.permission_ids)
            dept_ids = set(data.dept_ids)
            if permission_ids:
                await self._ensure_permissions_exist(permission_ids)
            if dept_ids:
                await self._ensure_depts_exist(dept_ids)
            role.change(data.name, data.data_scope, data.description, current_user.user_id)
            role.change_status(data.status, current_user.user_id)
            role.set_permissions(permission_ids, current_user.user_id)
            role.set_depts(dept_ids, current_user.user_id)
            await self.role_repo.update(role)
        # 整体替换：名称/权限/数据范围变更都影响持有者快照（多清无害）
        await self.event_bus.publish(RoleChanged(id=EventId.new(), role_id=role.id))

    @requires_permission('iam:role:delete')
    async def delete_role(self, role_id: RoleId, current_user: CurrentUser) -> None:
        async with self.in_transaction():
            role = await self._load_accessible(role_id, current_user)
            role.delete(current_user.user_id)
            await self.role_repo.update(role)
        await self.event_bus.publish(RoleChanged(id=EventId.new(), role_id=role_id))

    # ---------------- 读 ----------------
    @requires_permission('iam:role:read')
    async def get_role(self, role_id: RoleId, current_user: CurrentUser) -> RoleDetailOut:
        role = await self.role_repo.get(role_id)
        if role is None or role.status is StatusEnum.DELETED:
            raise RoleNotFoundException(f'角色不存在：{role_id}')
        return RoleDetailOut(
            id=role.id,
            code=role.code,
            name=role.name,
            data_scope=role.data_scope,
            status=role.status,
            description=role.description,
            permission_ids=list(role.permission_ids),
            dept_ids=list(role.custom_dept_ids),
        )

    @requires_permission('iam:role:read')
    async def get_all_roles(self, current_user: CurrentUser) -> list[RoleOut]:
        roles = await self.role_repo.get_all()
        return [
            RoleOut(id=r.id, code=r.code, name=r.name, data_scope=r.data_scope,
                    status=r.status, description=r.description)
            for r in roles
        ]

    # ---------------- 内部 ----------------
    async def _load_accessible(self, role_id: RoleId, current_user: CurrentUser) -> Role:
        role = await self.role_repo.get(role_id)
        if role is None or role.status is StatusEnum.DELETED:
            raise RoleNotFoundException(f'角色不存在：{role_id}')
        if not await self.role_access_service.can_access([role_id], current_user):
            raise PermissionDeniedException('无权访问该角色')
        return role

    async def _ensure_permissions_exist(self, permission_ids: set[PermissionId]) -> None:
        found = await self.permission_repo.get_by_ids(list(permission_ids))
        if len(found) != len(permission_ids):
            raise PermissionNotFoundException('存在无效的权限 id')

    async def _ensure_depts_exist(self, dept_ids: set[DeptId]) -> None:
        found = await self.dept_repo.get_by_ids(list(dept_ids))
        if len(found) != len(dept_ids):
            raise DeptNotFoundException('存在无效的部门 id')
