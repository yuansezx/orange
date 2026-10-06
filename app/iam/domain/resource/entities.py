from datetime import datetime, UTC

from pydantic import model_validator

from app.core.domain.entities import AuditableEntity
from app.iam.domain.resource.exceptions import InvalidResourceCodeException
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import ResourceId, UserId


class Resource(AuditableEntity[UserId]):
    """资源目录条目（扁平）。

    资源=名词（user/role/dept…），模块内 `code` 唯一；`module` 用于分组，不建模块表。
    权限标识 = `module:resource:action`。
    """

    id: ResourceId
    module: str  # 模块代号，如 'iam'
    code: str  # 模块内唯一，如 'user'
    name: str
    description: str | None = None
    status: StatusEnum

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
