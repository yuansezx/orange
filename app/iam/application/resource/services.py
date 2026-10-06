from datetime import datetime, UTC

from app.core.domain.units_of_work import InTransactionType
from app.iam.application.resource.dto import (
    CatalogModuleOut,
    CatalogOut,
    CatalogPermissionOut,
    CatalogResourceOut,
    CreatePermissionIn,
    CreateResourceIn,
    RegisterResourceIn,
    UpdatePermissionIn,
    UpdateResourceIn,
)
from app.iam.application.resource.exceptions import (
    PermissionActionConflictException,
    PermissionNotFoundException,
    ResourceCodeConflictException,
    ResourceNotFoundException,
)
from app.iam.domain.permission.entities import Permission
from app.iam.domain.permission.repositories import PermissionRepository
from app.iam.domain.resource.entities import Resource
from app.iam.domain.resource.repositories import ResourceRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId, UserId


class ResourceApplicationService:
    """资源 + 权限目录：代码声明注册 / 后台补充 / 目录读取。

    permission 无独立生命周期（身份从属于 resource），故两个仓储同一个服务持有。
    """

    def __init__(self, in_transaction: InTransactionType,
                 resource_repo: ResourceRepository,
                 permission_repo: PermissionRepository) -> None:
        self.in_transaction = in_transaction
        self.resource_repo = resource_repo
        self.permission_repo = permission_repo

    # ---------------- 代码声明（幂等注册） ----------------
    async def register_resource(self, data: RegisterResourceIn, operator_id: UserId) -> Resource:
        async with self.in_transaction():
            return await self._register_resource(data, operator_id)

    async def register_resources(self, declarations: list[RegisterResourceIn], operator_id: UserId) -> None:
        """批量注册，单事务原子。

        已知限制：代码声明被重命名/删除后，旧行残留且仍 ACTIVE（不再被声明），此处不对账；
        将来可加 source 标记（declared/admin）+ 对账 pass 处理。
        """
        async with self.in_transaction():
            for data in declarations:
                await self._register_resource(data, operator_id)

    # ---------------- 后台补充 ----------------
    async def create_resource(self, data: CreateResourceIn, operator_id: UserId) -> ResourceId:
        async with self.in_transaction():
            if await self.resource_repo.get_by_module_and_code(data.module, data.code):
                raise ResourceCodeConflictException(f'资源已存在：{data.module}:{data.code}')
            resource = await self.resource_repo.create(Resource(
                id=ResourceId.new(),
                module=data.module,
                code=data.code,
                name=data.name,
                description=data.description,
                status=StatusEnum.ACTIVE,
                created_at=datetime.now(UTC),
                created_by=operator_id,
            ))
            return resource.id

    async def create_permission(self, data: CreatePermissionIn, operator_id: UserId) -> PermissionId:
        async with self.in_transaction():
            resource = await self.resource_repo.get(data.resource_id)
            if resource is None or resource.status is StatusEnum.DELETED:
                raise ResourceNotFoundException(f'资源不存在：{data.resource_id}')
            if await self.permission_repo.get_by_resource_and_action(data.resource_id, data.action):
                raise PermissionActionConflictException(
                    f'权限已存在：{resource.full_code()}:{data.action}')
            permission = await self.permission_repo.create(Permission(
                id=PermissionId.new(),
                resource_id=data.resource_id,
                action=data.action,
                name=data.name,
                description=data.description,
                status=StatusEnum.ACTIVE,
                created_at=datetime.now(UTC),
                created_by=operator_id,
            ))
            return permission.id

    async def update_resource(self, data: UpdateResourceIn, operator_id: UserId) -> None:
        async with self.in_transaction():
            resource = await self.resource_repo.get(data.id)
            if resource is None:
                raise ResourceNotFoundException(f'资源不存在：{data.id}')
            if data.name is not None or data.description is not None:
                resource.change(
                    data.name if data.name is not None else resource.name,
                    data.description if data.description is not None else resource.description,
                    operator_id,
                )
            if data.status is not None:
                resource.change_status(data.status, operator_id)
            await self.resource_repo.update(resource)

    async def update_permission(self, data: UpdatePermissionIn, operator_id: UserId) -> None:
        async with self.in_transaction():
            permission = await self.permission_repo.get(data.id)
            if permission is None:
                raise PermissionNotFoundException(f'权限不存在：{data.id}')
            if data.name is not None or data.description is not None:
                permission.change(
                    data.name if data.name is not None else permission.name,
                    data.description if data.description is not None else permission.description,
                    operator_id,
                )
            if data.status is not None:
                permission.change_status(data.status, operator_id)
            await self.permission_repo.update(permission)

    async def delete_resource(self, resource_id: ResourceId, operator_id: UserId) -> None:
        async with self.in_transaction():
            resource = await self.resource_repo.get(resource_id)
            if resource is None:
                raise ResourceNotFoundException(f'资源不存在：{resource_id}')
            resource.delete(operator_id)
            await self.resource_repo.update(resource)

    async def delete_permission(self, permission_id: PermissionId, operator_id: UserId) -> None:
        async with self.in_transaction():
            permission = await self.permission_repo.get(permission_id)
            if permission is None:
                raise PermissionNotFoundException(f'权限不存在：{permission_id}')
            permission.delete(operator_id)
            await self.permission_repo.update(permission)

    # ---------------- 读取 ----------------
    async def get_catalog(self, include_disabled: bool = False) -> CatalogOut:
        """返回「模块 → 资源 → 权限」三级结构（两条查询 + 内存分组，无 N+1）。"""
        resources = await self.resource_repo.get_all()
        if not include_disabled:
            resources = [r for r in resources if r.status is not StatusEnum.DISABLED]

        permissions = await self.permission_repo.get_by_resource_ids([r.id for r in resources])
        if not include_disabled:
            permissions = [p for p in permissions if p.status is not StatusEnum.DISABLED]

        perms_by_resource: dict[ResourceId, list[Permission]] = {}
        for p in permissions:
            perms_by_resource.setdefault(p.resource_id, []).append(p)

        modules: dict[str, CatalogModuleOut] = {}
        for r in resources:
            module_out = modules.setdefault(r.module, CatalogModuleOut(module=r.module))
            module_out.resources.append(CatalogResourceOut(
                id=r.id,
                module=r.module,
                code=r.code,
                key=r.full_code(),
                name=r.name,
                description=r.description,
                status=r.status,
                permissions=[CatalogPermissionOut(
                    id=p.id,
                    action=p.action,
                    key=p.full_code(r),
                    name=p.name,
                    description=p.description,
                    status=p.status,
                ) for p in perms_by_resource.get(r.id, [])],
            ))
        return CatalogOut(modules=list(modules.values()))

    # ---------------- 内部方法 ----------------
    async def _register_resource(self, data: RegisterResourceIn, operator_id: UserId) -> Resource:
        """幂等 upsert：按自然键查 → 建或改。假定事务已开。"""
        resource = await self.resource_repo.get_by_module_and_code(data.module, data.code)
        if resource is None:
            resource = await self.resource_repo.create(Resource(
                id=ResourceId.new(),
                module=data.module,
                code=data.code,
                name=data.name,
                description=data.description,
                status=StatusEnum.ACTIVE,
                created_at=datetime.now(UTC),
                created_by=operator_id,
            ))
        else:
            changed = False
            if resource.name != data.name or resource.description != data.description:
                resource.change(data.name, data.description, operator_id)
                changed = True
            if resource.status is not StatusEnum.ACTIVE:
                resource.change_status(StatusEnum.ACTIVE, operator_id)
                changed = True
            if changed:
                await self.resource_repo.update(resource)

        for p in data.permissions:
            permission = await self.permission_repo.get_by_resource_and_action(resource.id, p.action)
            if permission is None:
                await self.permission_repo.create(Permission(
                    id=PermissionId.new(),
                    resource_id=resource.id,
                    action=p.action,
                    name=p.name,
                    description=p.description,
                    status=StatusEnum.ACTIVE,
                    created_at=datetime.now(UTC),
                    created_by=operator_id,
                ))
            else:
                changed = False
                if permission.name != p.name or permission.description != p.description:
                    permission.change(p.name, p.description, operator_id)
                    changed = True
                if permission.status is not StatusEnum.ACTIVE:
                    permission.change_status(StatusEnum.ACTIVE, operator_id)
                    changed = True
                if changed:
                    await self.permission_repo.update(permission)
        return resource
