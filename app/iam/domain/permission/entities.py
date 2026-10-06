from datetime import datetime, UTC

from pydantic import model_validator

from app.core.domain.entities import AuditableEntity
from app.iam.domain.permission.exceptions import InvalidPermissionActionException
from app.iam.domain.resource.entities import Resource
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import PermissionId, ResourceId, UserId


class Permission(AuditableEntity[UserId]):
    """权限目录条目 = 某资源上的一个操作（action）。

    `action` 为自由字符串（create/read/export/reset-password…），资源内唯一，不设枚举。
    完整标识 `module:resource:action` 运行时派生（见 full_code），不落库。
    """

    id: PermissionId
    resource_id: ResourceId
    action: str
    name: str
    description: str | None = None
    status: StatusEnum

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
        """软删除：只置 status=DELETED 并记录删除人/时间，不物理删除。"""
        self.change_status(StatusEnum.DELETED, operator_id)
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)
