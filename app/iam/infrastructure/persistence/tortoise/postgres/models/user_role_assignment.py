from future_uuid import uuid7
from tortoise import fields

from app.core.infrastructure.persistence.tortoise.models import AuditableModel
from app.iam.domain.shared.enums import StatusEnum


class UserRoleAssignmentModel(AuditableModel):
    """user_role 关系表（一行/状态翻转：一个 (user_id, role_id) 只一行）。"""

    id = fields.UUIDField(primary_key=True, default=uuid7)
    user_id = fields.UUIDField()
    role_id = fields.UUIDField()
    status = fields.CharEnumField(StatusEnum, max_length=50)

    class Meta:
        table = 'iam_user_role'
        unique_together = (('user_id', 'role_id'),)
