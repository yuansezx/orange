from future_uuid import uuid7
from tortoise import fields

from app.core.infrastructure.persistence.tortoise.models import AuditableModel
from app.iam.domain.role.enums import DataScopeEnum
from app.iam.domain.shared.enums import StatusEnum


class RoleModel(AuditableModel):
    """role 聚合的表模型。code 唯一标识，name 仅作昵称/展示。"""

    id = fields.UUIDField(primary_key=True, default=uuid7)
    code = fields.CharField(max_length=64, unique=True)
    name = fields.CharField(max_length=128)
    data_scope = fields.CharEnumField(DataScopeEnum, max_length=50)
    status = fields.CharEnumField(StatusEnum, max_length=50)
    description = fields.TextField(null=True)

    class Meta:
        table = 'iam_role'
