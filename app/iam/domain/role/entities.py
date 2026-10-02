from dataclasses import dataclass

from app.core.domain.entities import AuditableEntity
from app.iam.domain.role.enums import DataScopeEnum
from app.iam.domain.shared.value_objects import RoleId, DeptId
from app.iam.domain.shared.enums import StatusEnum


@dataclass
class RoleFilter:
    status: StatusEnum | None = None
    keyword: str | None = None


class Role(AuditableEntity):
    id: RoleId
    name: str
    data_scope: DataScopeEnum
    custom_dept_ids: list[DeptId]
    status: StatusEnum
    remark: str | None = None
