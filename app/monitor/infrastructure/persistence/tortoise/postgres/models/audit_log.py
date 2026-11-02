from future_uuid import uuid7
from tortoise import fields, models

from app.monitor.domain.audit_log.enums import AuditResultEnum


class AuditLogModel(models.Model):
    """审计日志表模型（只追加）。

    与领域实体 `app.monitor.domain.audit_log.entities.AuditLog` 分离：
    表里额外有 `persisted_at`（实际落库时间），领域实体只关心 `occurred_at`。
    操作人/目标都是**快照**（不建 FK），目标或用户被删除不影响历史记录。
    """

    id = fields.UUIDField(primary_key=True, default=uuid7)
    occurred_at = fields.DatetimeField()
    # 明确为“落库时间”，避免与 iam 实体的 created_at（业务创建时间）混淆
    persisted_at = fields.DatetimeField(auto_now_add=True)

    module = fields.CharField(max_length=64)
    resource = fields.CharField(max_length=64)
    action = fields.CharField(max_length=64)

    summary = fields.CharField(max_length=512)

    target_type = fields.CharField(max_length=64, null=True)
    target_id = fields.CharField(max_length=128, null=True)
    target_name = fields.CharField(max_length=255, null=True)

    operator_id = fields.UUIDField(null=True)
    operator_username = fields.CharField(max_length=64, null=True)
    operator_nickname = fields.CharField(max_length=128, null=True)

    result = fields.CharEnumField(AuditResultEnum, max_length=50)
    error_code = fields.CharField(max_length=128, null=True)
    error_message = fields.TextField(null=True)

    request_id = fields.CharField(max_length=64, null=True)
    ip = fields.CharField(max_length=64, null=True)
    user_agent = fields.TextField(null=True)

    detail = fields.JSONField(default=dict)

    class Meta:
        table = 'monitor_audit_log'
        indexes = (
            ('occurred_at',),
            ('module', 'resource', 'action'),
            ('operator_id', 'occurred_at'),
            ('target_type', 'target_id'),
            ('request_id',),
        )
