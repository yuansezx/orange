from app.core.domain.entities import AuditableEntity
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import Email, Phone, DeptId, UserId


class Dept(AuditableEntity):
    id: DeptId
    name: str
    parent_id: DeptId | None = None
    leader_id: UserId | None = None
    email: Email | None = None
    phone: Phone | None = None
    status: StatusEnum
    description: str | None = None
