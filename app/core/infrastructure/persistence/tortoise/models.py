from tortoise import Model, fields


class AuditableModel(Model):
    """ORM 侧审计基类（对应领域侧 app.core.domain.entities.AuditableEntity）。

    abstract = True：本身不建表，仅供各模块的表模型继承以复用审计字段。
    """
    created_at = fields.DatetimeField()
    created_by = fields.UUIDField()
    updated_at = fields.DatetimeField(null=True)
    updated_by = fields.UUIDField(null=True)
    deleted_at = fields.DatetimeField(null=True)
    deleted_by = fields.UUIDField(null=True)

    class Meta:
        abstract = True
