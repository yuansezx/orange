from future_uuid import uuid7
from tortoise import fields

from app.core.infrastructure.persistence.tortoise.models import AuditableModel
from app.iam.domain.shared.enums import StatusEnum


class DeptModel(AuditableModel):
    """dept 聚合的表模型（与领域实体 app.iam.domain.dept.entities.Dept 分离）。

    parent_id 用普通 UUID 列（非 FK），与 UserModel.dept_id 一致：引用走 ID，不加库级外键。
    """

    id = fields.UUIDField(primary_key=True, default=uuid7)
    name = fields.CharField(max_length=64)
    parent_id = fields.UUIDField(null=True)
    leader_id = fields.UUIDField(null=True)
    email = fields.CharField(max_length=255, null=True)
    phone = fields.CharField(max_length=20, null=True)
    # 枚举列长度给足余量（PG varchar 只存实际长度）
    status = fields.CharEnumField(StatusEnum, max_length=50)
    remark = fields.TextField(null=True)

    class Meta:
        table = 'iam_dept'
