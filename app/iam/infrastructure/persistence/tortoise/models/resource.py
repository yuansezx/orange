from future_uuid import uuid7
from tortoise import fields

from app.core.infrastructure.persistence.tortoise.models import AuditableModel
from app.iam.domain.shared.enums import StatusEnum


class ResourceModel(AuditableModel):
    """resource 目录的表模型（与领域实体 app.iam.domain.resource.entities.Resource 分离）。

    扁平结构 + module 分组字段，不建模块表；(module, code) 联合唯一。
    """

    id = fields.UUIDField(primary_key=True, default=uuid7)
    module = fields.CharField(max_length=64)
    code = fields.CharField(max_length=64)
    name = fields.CharField(max_length=128)
    description = fields.TextField(null=True)
    status = fields.CharEnumField(StatusEnum, max_length=50)

    class Meta:
        table = 'iam_resource'
        unique_together = (('module', 'code'),)
