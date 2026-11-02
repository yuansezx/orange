from __future__ import annotations

from datetime import datetime, UTC

from pydantic import Field, model_validator

from app.core.domain.entities import AuditableEntity
from app.iam.domain.resource.enums import SourceTypeEnum
from app.iam.domain.resource.exceptions import (
    InvalidPermissionActionException,
    InvalidResourceCodeException,
)
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId, UserId


class Permission(AuditableEntity[UserId]):
    """权限目录条目 = 某资源上的一个操作（action）——**Resource 聚合内实体**。

    身份从属于资源（`(resource_id, action)` 唯一），不独立存在。
    `action` 为自由字符串（create/read/export/reset-password…），资源内唯一，不设枚举。
    完整标识 `module:resource:action` 运行时派生（见 `full_code`），不落库。
    """

    id: PermissionId
    resource_id: ResourceId
    action: str
    name: str
    description: str | None = None
    status: StatusEnum
    permission_type: SourceTypeEnum

    @model_validator(mode='after')
    def _check_action(self):
        """action 非空且不含分隔符 ':'。"""
        if not self.action or ':' in self.action:
            raise InvalidPermissionActionException(f'权限 action 非法：{self.action!r}')
        return self

    def full_code(self, resource: Resource) -> str:
        return f'{resource.module}:{resource.code}:{self.action}'

    def change(self, name: str, description: str | None, operator_id: UserId) -> None:
        self.name = name
        self.description = description
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def change_status(self, status: StatusEnum, operator_id: UserId) -> None:
        self.status = status
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def delete(self, operator_id: UserId) -> None:
        """软删除：只写 deleted_at/by，不物理删除，不动 status。"""
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def restore(self, operator_id: UserId) -> None:
        """清删除痕迹（代码重新声明时幂等复活）。"""
        self.deleted_at = None
        self.deleted_by = None
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)


class Resource(AuditableEntity[UserId]):
    """资源目录条目（**聚合根**）：一个名词 + 其上的权限动作集。

    资源=名词（user/role/dept…），模块内 `code` 唯一；`module` 用于分组，不建模块表。
    `permissions` 是聚合内实体，随聚合整体装配/保存。
    """

    id: ResourceId
    module: str  # 模块代号，如 'iam'
    code: str  # 模块内唯一，如 'user'
    name: str
    description: str | None = None
    status: StatusEnum
    resource_type: SourceTypeEnum
    permissions: list[Permission] = Field(default_factory=list)

    @model_validator(mode='after')
    def _check_key(self):
        """module/code 非空且不含分隔符 ':'（格式不变式只在此处落地）。"""
        if not self.module or ':' in self.module:
            raise InvalidResourceCodeException(f'资源 module 非法：{self.module!r}')
        if not self.code or ':' in self.code:
            raise InvalidResourceCodeException(f'资源 code 非法：{self.code!r}')
        return self

    def full_code(self) -> str:
        return f'{self.module}:{self.code}'

    # ---------------- 权限（聚合内实体） ----------------
    def get_permission(self, action: str) -> Permission | None:
        return next((p for p in self.permissions if p.action == action), None)

    def get_permission_by_id(self, permission_id: PermissionId) -> Permission | None:
        return next((p for p in self.permissions if p.id == permission_id), None)

    def declare_permission(self, action: str, name: str, description: str | None,
                           permission_type: SourceTypeEnum, operator_id: UserId) -> Permission:
        """**幂等**声明一个权限动作：已存在（含软删）则更新属性并复活，否则新建。

        幂等是为了 bootstrap 反复注册——重声明不新插、不撞 `(resource_id, action)` 唯一约束。
        复活时归属以**本次声明方**为准（代码声明会接管一个原本 custom 的动作）。
        需要「已存在即冲突」的语义时，由调用方先 `get_permission` 判断。
        """
        existing = self.get_permission(action)
        if existing is not None:
            existing.change(name, description, operator_id)
            existing.permission_type = permission_type
            if existing.is_deleted:
                existing.restore(operator_id)
            if existing.status is not StatusEnum.ACTIVE:
                existing.change_status(StatusEnum.ACTIVE, operator_id)
            return existing

        permission = Permission(
            id=PermissionId.new(),
            resource_id=self.id,
            action=action,
            name=name,
            description=description,
            status=StatusEnum.ACTIVE,
            permission_type=permission_type,
            created_at=datetime.now(UTC),
            created_by=operator_id,
        )
        self.permissions.append(permission)
        return permission

    # ---------------- 状态 ----------------
    def change(self, name: str, description: str | None, operator_id: UserId) -> None:
        self.name = name
        self.description = description
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def change_status(self, status: StatusEnum, operator_id: UserId) -> None:
        self.status = status
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def delete(self, operator_id: UserId) -> None:
        """软删除自身，并**级联**软删聚合内仍存活的权限（组合关系）。

        已单独软删的权限保持原删除时间：资源恢复时据此只复活「随资源一起删」的那批。
        """
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)
        for permission in self.permissions:
            if not permission.is_deleted:
                permission.delete(operator_id)

    def restore(self, operator_id: UserId) -> None:
        """清自身删除痕迹（代码重新声明时幂等复活）。聚合内权限各自按声明复活。"""
        self.deleted_at = None
        self.deleted_by = None
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)
