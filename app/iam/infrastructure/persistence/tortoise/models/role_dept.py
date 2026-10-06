from future_uuid import uuid7
from tortoise import Model, fields


class RoleDeptModel(Model):
    """角色-部门关系表（CUSTOM 数据范围用；裸映射：无 status/审计，移除即物理删）。"""

    id = fields.UUIDField(primary_key=True, default=uuid7)
    role_id = fields.UUIDField()
    dept_id = fields.UUIDField()

    class Meta:
        table = 'iam_role_dept'
        unique_together = (('role_id', 'dept_id'),)
