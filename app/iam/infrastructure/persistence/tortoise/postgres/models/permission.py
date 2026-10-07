from future_uuid import uuid7
from tortoise import fields

from app.core.infrastructure.persistence.tortoise.models import AuditableModel
from app.iam.domain.shared.enums import StatusEnum


class PermissionModel(AuditableModel):
    """permission 目录的表模型（与领域实体 app.iam.domain.permission.entities.Permission 分离）。

    resource_id 用普通 UUID 列（非 FK），引用走 ID。完整标识 `module:resource:action`
    运行时派生，不落库；(resource_id, action) 联合唯一。
    """

    id = fields.UUIDField(primary_key=True, default=uuid7)
    resource_id = fields.UUIDField()
    action = fields.CharField(max_length=64)
    name = fields.CharField(max_length=128)
    description = fields.TextField(null=True)
    status = fields.CharEnumField(StatusEnum, max_length=50)

    class Meta:
        table = 'iam_permission'
        unique_together = (('resource_id', 'action'),)
