from future_uuid import uuid7
from tortoise import Model, fields


class RolePermissionModel(Model):
    """角色-权限关系表（裸映射：无 status/审计，移除即物理删）。

    生命周期完全由 Role 聚合掌控（见 RoleRepository）；跨聚合不级联。
    """

    id = fields.UUIDField(primary_key=True, default=uuid7)
    role_id = fields.UUIDField()
    permission_id = fields.UUIDField()

    class Meta:
        table = 'iam_role_permission'
        unique_together = (('role_id', 'permission_id'),)
