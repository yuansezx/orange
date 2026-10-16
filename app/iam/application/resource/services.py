from datetime import datetime, UTC

from app.core.domain.units_of_work import InTransactionType
from app.iam.application.common.decorators import requires_permission
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
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.resource.entities import Permission, Resource
from app.iam.domain.resource.repositories import ResourceRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId, UserId


class ResourceApplicationService:
    """资源 + 权限目录（**Resource 聚合**）：代码声明注册 / 后台补充 / 目录读取。

    permission 是聚合内实体（身份从属于资源）——一律 load 聚合 → 实体方法变更 → update 整体落库。
    """

    def __init__(self, in_transaction: InTransactionType,
                 resource_repo: ResourceRepository) -> None:
        self.in_transaction = in_transaction
        self.resource_repo = resource_repo

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
            resource = await self._load(data.resource_id)
            if resource.get_permission(data.action) is not None:
                raise PermissionActionConflictException(
                    f'权限已存在：{resource.full_code()}:{data.action}')
            permission = resource.declare_permission(
                data.action, data.name, data.description, operator_id)
            await self.resource_repo.update(resource)
            return permission.id

    async def update_resource(self, data: UpdateResourceIn, operator_id: UserId) -> None:
        async with self.in_transaction():
            resource = await self._load(data.id)
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
            resource, permission = await self._load_permission(data.id)
            permission.change(
                data.name if data.name is not None else permission.name,
                data.description if data.description is not None else permission.description,
                operator_id,
            )
            if data.status is not None:
                permission.change_status(data.status, operator_id)
            await self.resource_repo.update(resource)

    async def delete_resource(self, resource_id: ResourceId, operator_id: UserId) -> None:
        async with self.in_transaction():
            resource = await self._load(resource_id)
            resource.delete(operator_id)  # 级联软删聚合内权限
            await self.resource_repo.update(resource)

    async def delete_permission(self, permission_id: PermissionId, operator_id: UserId) -> None:
        async with self.in_transaction():
            resource, permission = await self._load_permission(permission_id)
            permission.delete(operator_id)
            await self.resource_repo.update(resource)

    # ---------------- 读取 ----------------
    @requires_permission(('iam:resource:read', 'iam:permission:read'), 'iam:role:read')
    async def get_catalog(self, current_user: CurrentUser, include_disabled: bool = False) -> CatalogOut:
        """返回「模块 → 资源 → 权限」三级结构（装配聚合 + 内存分组，无 N+1）。"""
        modules: dict[str, CatalogModuleOut] = {}
        for resource in await self.resource_repo.get_all():
            if resource.status is StatusEnum.DELETED:
                continue
            if not include_disabled and resource.status is StatusEnum.DISABLED:
                continue
            permissions = [
                p for p in resource.permissions
                if p.status is not StatusEnum.DELETED
                and (include_disabled or p.status is not StatusEnum.DISABLED)
            ]
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

    # ---------------- 内部方法 ----------------
    async def _load(self, resource_id: ResourceId) -> Resource:
        resource = await self.resource_repo.get(resource_id)
        if resource is None or resource.status is StatusEnum.DELETED:
            raise ResourceNotFoundException(f'资源不存在：{resource_id}')
        return resource

    async def _load_permission(self, permission_id: PermissionId) -> tuple[Resource, Permission]:
        resource = await self.resource_repo.get_by_permission_id(permission_id)
        permission = resource.get_permission_by_id(permission_id) if resource else None
        if resource is None or permission is None:
            raise PermissionNotFoundException(f'权限不存在：{permission_id}')
        return resource, permission

    async def _register_resource(self, data: RegisterResourceIn, operator_id: UserId) -> Resource:
        """幂等 upsert：按自然键查 → 建或改。假定事务已开。"""
        resource = await self.resource_repo.get_by_module_and_code(data.module, data.code)
        if resource is None:
            resource = Resource(
                id=ResourceId.new(),
                module=data.module,
                code=data.code,
                name=data.name,
                description=data.description,
                status=StatusEnum.ACTIVE,
                created_at=datetime.now(UTC),
                created_by=operator_id,
            )
            for p in data.permissions:
                resource.declare_permission(p.action, p.name, p.description, operator_id)
            return await self.resource_repo.create(resource)

        if resource.name != data.name or resource.description != data.description:
            resource.change(data.name, data.description, operator_id)
        if resource.status is not StatusEnum.ACTIVE:
            resource.change_status(StatusEnum.ACTIVE, operator_id)
        for p in data.permissions:
            resource.declare_permission(p.action, p.name, p.description, operator_id)
        await self.resource_repo.update(resource)
        return resource
