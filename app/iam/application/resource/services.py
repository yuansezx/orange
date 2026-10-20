from datetime import datetime, UTC
from collections.abc import Iterable

from loguru import logger

from app.core.domain.event_bus import EventBus
from app.core.domain.units_of_work import InTransactionType
from app.core.domain.value_objects import EventId
from app.iam.application.common.decorators import requires_permission
from app.iam.application.common.dto import AuditOut
from app.iam.application.common.queries import UsersAffectedByPermissionChangeQuery
from app.iam.application.common.services import AuditService
from app.iam.application.resource.dto import (
    CatalogModuleOut,
    CatalogOut,
    CatalogPermissionOut,
    CatalogResourceOut,
    CreatePermissionIn,
    CreateResourceIn,
    PermissionListItemOut,
    PermissionOut,
    RegisterResourceIn,
    ResourceOut,
    UpdatePermissionIn,
    UpdateResourceIn,
)
from app.iam.application.resource.exceptions import (
    PermissionActionConflictException,
    PermissionNotDeletedException,
    PermissionNotFoundException,
    ResourceCodeConflictException,
    ResourceNotDeletedException,
    ResourceNotFoundException,
    SystemPermissionReadOnlyException,
    SystemResourceReadOnlyException,
)
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.resource.entities import Permission, Resource
from app.iam.domain.resource.enums import SourceTypeEnum
from app.iam.domain.resource.events import ResourceChanged
from app.iam.domain.resource.repositories import ResourceRepository
from app.iam.domain.role.repositories import RoleRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId, UserId


def _resource_out(resource: Resource, audit: AuditOut,
                  permissions: Iterable[PermissionOut] = ()) -> ResourceOut:
    return ResourceOut(
        id=resource.id,
        module=resource.module,
        code=resource.code,
        key=resource.full_code(),
        name=resource.name,
        description=resource.description,
        status=resource.status,
        resource_type=resource.resource_type,
        created_at=resource.created_at,
        updated_at=resource.updated_at,
        deleted_at=resource.deleted_at,
        permissions=list(permissions),
        **audit.model_dump(),
    )


def _permission_out(resource: Resource, permission: Permission, audit: AuditOut) -> PermissionOut:
    return PermissionOut(
        id=permission.id,
        resource_id=permission.resource_id,
        action=permission.action,
        key=permission.full_code(resource),
        name=permission.name,
        description=permission.description,
        status=permission.status,
        permission_type=permission.permission_type,
        created_at=permission.created_at,
        updated_at=permission.updated_at,
        deleted_at=permission.deleted_at,
        **audit.model_dump(),
    )


def _ensure_custom_resource(resource: Resource) -> None:
    if resource.resource_type is SourceTypeEnum.SYSTEM:
        raise SystemResourceReadOnlyException('系统声明的资源由代码维护，后台只读')


def _ensure_custom_permission(permission: Permission) -> None:
    if permission.permission_type is SourceTypeEnum.SYSTEM:
        raise SystemPermissionReadOnlyException('系统声明的权限由代码维护，后台只读')


class ResourceApplicationService:
    """资源 + 权限目录（**Resource 聚合**）：代码声明注册 / 对账 / 后台补充 / 目录读取。

    permission 是聚合内实体（身份从属于资源）——一律 load 聚合 → 实体方法变更 → update 整体落库。
    SYSTEM 条目由代码声明拥有、后台只读；CUSTOM 条目可由后台增删改。
    """

    def __init__(self, in_transaction: InTransactionType,
                 resource_repo: ResourceRepository,
                 role_repo: RoleRepository,
                 audit_service: AuditService,
                 permission_users_query: UsersAffectedByPermissionChangeQuery,
                 event_bus: EventBus) -> None:
        self.in_transaction = in_transaction
        self.resource_repo = resource_repo
        self.role_repo = role_repo
        self.audit_service = audit_service
        self.permission_users_query = permission_users_query
        self.event_bus = event_bus

    # ---------------- 代码声明（幂等注册 + 对账） ----------------
    async def register_resource(self, data: RegisterResourceIn, operator_id: UserId) -> Resource:
        async with self.in_transaction():
            return await self._register_resource(data, operator_id)

    async def register_resources(self, module: str, declarations: list[RegisterResourceIn],
                                 operator_id: UserId) -> None:
        """批量注册，单事务原子；随后对账：本模块中已无代码声明的 SYSTEM 条目软删。

        软删而非硬删：保留 id 与角色引用，声明重新出现时 `declare_permission` 复活同一行、
        角色授权自动恢复。CUSTOM 条目一律不碰。
        """
        if {d.module for d in declarations} - {module}:
            raise ValueError(f'声明模块必须全部为 {module!r}')

        stale_permission_ids: list[set[PermissionId]] = []
        async with self.in_transaction():
            for data in declarations:
                await self._register_resource(data, operator_id)
            stale_permission_ids = await self._reconcile(module, declarations, operator_id)

        for ids in stale_permission_ids:
            await self._publish(ids)

    # ---------------- 后台补充：资源 ----------------
    @requires_permission('iam:resource:create')
    async def create_resource(self, data: CreateResourceIn, current_user: CurrentUser) -> ResourceOut:
        async with self.in_transaction():
            # 软删仍占位（唯一键仍在）→ 冲突判定显式含已删
            if await self.resource_repo.get_by_module_and_code(
                    data.module, data.code, include_deleted=True):
                raise ResourceCodeConflictException(f'资源已存在：{data.module}:{data.code}')
            resource = await self.resource_repo.create(Resource(
                id=ResourceId.new(),
                module=data.module,
                code=data.code,
                name=data.name,
                description=data.description,
                status=StatusEnum.ACTIVE,
                resource_type=SourceTypeEnum.CUSTOM,
                created_at=datetime.now(UTC),
                created_by=current_user.user_id,
            ))
        return _resource_out(resource, await self.audit_service.build(resource))

    @requires_permission('iam:resource:update')
    async def update_resource(self, data: UpdateResourceIn, current_user: CurrentUser) -> None:
        async with self.in_transaction():
            resource = await self._load(data.id)
            _ensure_custom_resource(resource)
            resource.change(data.name, data.description, current_user.user_id)
            await self.resource_repo.update(resource)

    @requires_permission('iam:resource:update')
    async def set_resource_status(self, resource_id: ResourceId, status: StatusEnum,
                                  current_user: CurrentUser) -> None:
        async with self.in_transaction():
            resource = await self._load(resource_id)
            _ensure_custom_resource(resource)
            resource.change_status(status, current_user.user_id)
            await self.resource_repo.update(resource)
        await self._publish(p.id for p in resource.permissions)

    @requires_permission('iam:resource:delete')
    async def delete_resource(self, resource_id: ResourceId, current_user: CurrentUser) -> None:
        async with self.in_transaction():
            resource = await self._load(resource_id)
            _ensure_custom_resource(resource)
            resource.delete(current_user.user_id)  # 级联软删聚合内权限
            await self.resource_repo.update(resource)
        await self._publish(p.id for p in resource.permissions)

    @requires_permission('iam:resource:delete')
    async def restore_resource(self, resource_id: ResourceId, current_user: CurrentUser) -> None:
        """恢复资源，只复活**随资源一起被删**的权限。

        此前单独软删的权限保持已删状态（删除时间早于资源），由权限回收站单独恢复。
        """
        async with self.in_transaction():
            resource = await self._load_any(resource_id)
            if not resource.is_deleted:
                raise ResourceNotDeletedException('资源未被删除，无需恢复')
            _ensure_custom_resource(resource)
            deleted_at = resource.deleted_at
            resource.restore(current_user.user_id)
            restored_ids: list[PermissionId] = []
            for permission in resource.permissions:
                if (permission.is_deleted and permission.deleted_at is not None
                        and deleted_at is not None and permission.deleted_at >= deleted_at):
                    permission.restore(current_user.user_id)
                    restored_ids.append(permission.id)
            await self.resource_repo.update(resource)
        await self._publish(restored_ids)

    @requires_permission('iam:resource:hard_delete')
    async def hard_delete_resource(self, resource_id: ResourceId, current_user: CurrentUser) -> None:
        """彻底删除（物理）——只允许对已软删行做；SYSTEM 墓碑也可清理，级联清角色引用。"""
        async with self.in_transaction():
            resource = await self._load_any(resource_id)
            if not resource.is_deleted:
                raise ResourceNotDeletedException('只能彻底删除已删除的资源')
            permission_ids = [p.id for p in resource.permissions]
            # 引用行即将随权限删除，事后再查不到持有者 → 事务内预取
            affected_user_ids = frozenset(
                await self.permission_users_query.resolve(permission_ids))
            await self.role_repo.remove_permissions(permission_ids)
            await self.resource_repo.hard_delete(resource.id)
        await self._publish(permission_ids, affected_user_ids=affected_user_ids)

    # ---------------- 后台补充：权限 ----------------
    @requires_permission('iam:permission:create')
    async def create_permission(self, data: CreatePermissionIn,
                                current_user: CurrentUser) -> PermissionOut:
        async with self.in_transaction():
            # 全量装配：已删的 action 仍占身份，需给出冲突而非撞唯一键
            resource = await self._load(data.resource_id, include_deleted_permissions=True)
            if resource.get_permission(data.action) is not None:
                raise PermissionActionConflictException(
                    f'权限已存在：{resource.full_code()}:{data.action}')
            permission = resource.declare_permission(
                data.action, data.name, data.description, SourceTypeEnum.CUSTOM,
                current_user.user_id)
            await self.resource_repo.update(resource)
        return _permission_out(
            resource, permission, await self.audit_service.build(permission))

    @requires_permission('iam:permission:update')
    async def update_permission(self, data: UpdatePermissionIn, current_user: CurrentUser) -> None:
        async with self.in_transaction():
            resource, permission = await self._load_permission(data.id)
            _ensure_custom_permission(permission)
            permission.change(data.name, data.description, current_user.user_id)
            await self.resource_repo.update(resource)

    @requires_permission('iam:permission:update')
    async def set_permission_status(self, permission_id: PermissionId, status: StatusEnum,
                                    current_user: CurrentUser) -> None:
        async with self.in_transaction():
            resource, permission = await self._load_permission(permission_id)
            _ensure_custom_permission(permission)
            permission.change_status(status, current_user.user_id)
            await self.resource_repo.update(resource)
        await self._publish([permission_id])

    @requires_permission('iam:permission:delete')
    async def delete_permission(self, permission_id: PermissionId,
                                current_user: CurrentUser) -> None:
        async with self.in_transaction():
            resource, permission = await self._load_permission(permission_id)
            _ensure_custom_permission(permission)
            permission.delete(current_user.user_id)
            await self.resource_repo.update(resource)
        await self._publish([permission_id])

    @requires_permission('iam:permission:delete')
    async def restore_permission(self, permission_id: PermissionId,
                                 current_user: CurrentUser) -> None:
        async with self.in_transaction():
            resource, permission = await self._load_permission(permission_id, include_deleted=True)
            if not permission.is_deleted:
                raise PermissionNotDeletedException('权限未被删除，无需恢复')
            _ensure_custom_permission(permission)
            permission.restore(current_user.user_id)
            await self.resource_repo.update(resource)
        await self._publish([permission_id])

    @requires_permission('iam:permission:hard_delete')
    async def hard_delete_permission(self, permission_id: PermissionId,
                                     current_user: CurrentUser) -> None:
        """彻底删除（物理）——只允许对已软删行做；SYSTEM 墓碑也可清理，级联清角色引用。"""
        async with self.in_transaction():
            _, permission = await self._load_permission(permission_id, include_deleted=True)
            if not permission.is_deleted:
                raise PermissionNotDeletedException('只能彻底删除已删除的权限')
            affected_user_ids = frozenset(
                await self.permission_users_query.resolve([permission_id]))
            await self.role_repo.remove_permissions([permission_id])
            await self.resource_repo.hard_delete_permission(permission_id)
        await self._publish([permission_id], affected_user_ids=affected_user_ids)

    # ---------------- 读取 ----------------
    @requires_permission(('iam:resource:read', 'iam:permission:read'), 'iam:role:read')
    async def get_catalog(self, current_user: CurrentUser) -> CatalogOut:
        """返回「模块 → 资源 → 权限」三级结构（装配聚合 + 内存分组，无 N+1）。

        只排除**已删**；**停用的照列**（停用 ≠ 删除，管理时要看得到才能启用）。
        """
        modules: dict[str, CatalogModuleOut] = {}
        # 缺省即：资源、聚合内权限都只装配未删的
        for resource in await self.resource_repo.get_all():
            permissions = resource.permissions
            module_out = modules.setdefault(resource.module, CatalogModuleOut(module=resource.module))
            module_out.resources.append(CatalogResourceOut(
                id=resource.id,
                module=resource.module,
                code=resource.code,
                key=resource.full_code(),
                name=resource.name,
                description=resource.description,
                status=resource.status,
                permissions=[CatalogPermissionOut(
                    id=p.id,
                    action=p.action,
                    key=p.full_code(resource),
                    name=p.name,
                    description=p.description,
                    status=p.status,
                ) for p in permissions],
            ))
        return CatalogOut(modules=list(modules.values()))

    @requires_permission('iam:resource:read', 'iam:permission:read')
    async def get_resources(self, current_user: CurrentUser,
                            status: StatusEnum | None = None,
                            deleted: bool = False,
                            include_deleted_permissions: bool = False) -> list[ResourceOut]:
        """扁平资源列表（含聚合内权限 + 审计）；`deleted` = 回收站。"""
        resources = await self.resource_repo.get_all(
            status, deleted, include_deleted_permissions=include_deleted_permissions)
        resource_audits = await self.audit_service.build_many(resources)
        permissions = [p for resource in resources for p in resource.permissions]
        permission_audits = iter(await self.audit_service.build_many(permissions))

        items: list[ResourceOut] = []
        for resource, audit in zip(resources, resource_audits):
            items.append(_resource_out(resource, audit, (
                _permission_out(resource, p, next(permission_audits))
                for p in resource.permissions
            )))
        return items

    @requires_permission('iam:permission:read', 'iam:resource:read')
    async def get_permissions(self, current_user: CurrentUser,
                              deleted: bool = False) -> list[PermissionListItemOut]:
        """扁平权限列表（含所属资源 + 审计）。

        `deleted=True` = 权限回收站：只列**资源仍存活**的已删权限。
        随资源一起被删的权限不单独出现，跟着资源恢复/彻底删除。
        """
        resources = await self.resource_repo.get_all(
            deleted=False, include_deleted_permissions=deleted)
        rows = [(resource, permission)
                for resource in resources
                for permission in resource.permissions
                if permission.is_deleted == deleted]
        audits = await self.audit_service.build_many([p for _, p in rows])

        items: list[PermissionListItemOut] = []
        for (resource, permission), audit in zip(rows, audits):
            out = _permission_out(resource, permission, audit)
            items.append(PermissionListItemOut(
                **out.model_dump(),
                resource_key=resource.full_code(),
                resource_name=resource.name,
            ))
        return items

    # ---------------- 内部方法 ----------------
    async def _publish(self, permission_ids: Iterable[PermissionId], *,
                       affected_user_ids: frozenset[UserId] | None = None) -> None:
        ids = frozenset(permission_ids)
        if not ids and affected_user_ids is None:
            return
        await self.event_bus.publish(ResourceChanged(
            id=EventId.new(), permission_ids=ids, affected_user_ids=affected_user_ids))

    async def _reconcile(self, module: str, declarations: list[RegisterResourceIn],
                         operator_id: UserId) -> list[set[PermissionId]]:
        """对账：本模块中不再被代码声明的 SYSTEM 资源/权限 → 软删。假定事务已开。

        返回每次变更受影响的权限 id 集（供调用方在提交后发快照失效事件）。
        """
        declared = {(d.module, d.code): {p.action for p in d.permissions}
                    for d in declarations}
        stale_groups: list[set[PermissionId]] = []
        resources = await self.resource_repo.get_by_module(
            module, include_deleted=True, include_deleted_permissions=True)

        for resource in resources:
            if resource.resource_type is not SourceTypeEnum.SYSTEM:
                continue

            key = (resource.module, resource.code)
            if key not in declared:
                if not resource.is_deleted:
                    resource.delete(operator_id)
                    await self.resource_repo.update(resource)
                    logger.warning('对账：SYSTEM 资源已无代码声明，软删 {!r}', resource.full_code())
                    stale_groups.append({p.id for p in resource.permissions})
                continue

            actions = declared[key]
            stale = [p for p in resource.permissions
                     if p.permission_type is SourceTypeEnum.SYSTEM
                     and p.action not in actions and not p.is_deleted]
            if not stale:
                continue
            for permission in stale:
                permission.delete(operator_id)
                logger.warning('对账：SYSTEM 权限已无代码声明，软删 {!r}',
                               permission.full_code(resource))
            await self.resource_repo.update(resource)
            stale_groups.append({p.id for p in stale})

        return stale_groups

    async def _load(self, resource_id: ResourceId, *,
                    include_deleted_permissions: bool = False) -> Resource:
        """写侧加载：仓储默认不返回已删资源/权限。"""
        resource = await self.resource_repo.get(
            resource_id, include_deleted_permissions=include_deleted_permissions)
        if resource is None:
            raise ResourceNotFoundException(f'资源不存在：{resource_id}')
        return resource

    async def _load_any(self, resource_id: ResourceId) -> Resource:
        """读侧加载：不惧已删（回收站恢复 / 彻底删除用）。"""
        resource = await self.resource_repo.get(
            resource_id, include_deleted=True, include_deleted_permissions=True)
        if resource is None:
            raise ResourceNotFoundException(f'资源不存在：{resource_id}')
        return resource

    async def _load_permission(self, permission_id: PermissionId, *,
                               include_deleted: bool = False) -> tuple[Resource, Permission]:
        # include_deleted=True 时连带装配已删权限（回收站恢复 / 彻底删除）
        resource = await self.resource_repo.get_by_permission_id(
            permission_id, include_deleted=include_deleted)
        permission = resource.get_permission_by_id(permission_id) if resource else None
        if resource is None or permission is None:
            raise PermissionNotFoundException(f'权限不存在：{permission_id}')
        return resource, permission

    async def _register_resource(self, data: RegisterResourceIn, operator_id: UserId) -> Resource:
        """幂等 upsert：按自然键查 → 建或改。假定事务已开。"""
        # 声明是写路径：已删资源要复活、已删权限要按 action 复活，故全量装配
        resource = await self.resource_repo.get_by_module_and_code(
            data.module, data.code, include_deleted=True, include_deleted_permissions=True)
        if resource is None:
            resource = Resource(
                id=ResourceId.new(),
                module=data.module,
                code=data.code,
                name=data.name,
                description=data.description,
                status=StatusEnum.ACTIVE,
                resource_type=SourceTypeEnum.SYSTEM,
                created_at=datetime.now(UTC),
                created_by=operator_id,
            )
            for p in data.permissions:
                resource.declare_permission(
                    p.action, p.name, p.description, SourceTypeEnum.SYSTEM, operator_id)
            return await self.resource_repo.create(resource)

        if resource.is_deleted:  # 代码重新声明 = 幂等复活
            resource.restore(operator_id)
        if resource.name != data.name or resource.description != data.description:
            resource.change(data.name, data.description, operator_id)
        if resource.status is not StatusEnum.ACTIVE:
            resource.change_status(StatusEnum.ACTIVE, operator_id)
        for p in data.permissions:
            resource.declare_permission(
                p.action, p.name, p.description, SourceTypeEnum.SYSTEM, operator_id)
        await self.resource_repo.update(resource)
        return resource
