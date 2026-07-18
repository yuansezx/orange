from dataclasses import dataclass

from app.core.domain.entities import AuditableEntity
from app.iam.domain.role.enums import DataScope
from app.iam.domain.shared.value_objects import RoleId, DeptId
from app.iam.domain.shared.enums import Status


@dataclass
class RoleFilter:
    status: Status | None = None
    keyword: str | None = None


class Role(AuditableEntity):
    id: RoleId
    name: str
    data_scope: DataScope
    custom_dept_ids: list[DeptId]
    status: Status
    remark: str | None = None
