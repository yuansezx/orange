# from tortoise import Model, fields
#
#
# class AuditableEntity(Model):
#     """带审计字段"""
#     created_at=fields.DatetimeField
#     created_by=fields.CharField()
#     updated_at: datetime | None = None
#     updated_by: IdType | None = None
#     deleted_at: datetime | None = None
#     deleted_by: IdType | None = None