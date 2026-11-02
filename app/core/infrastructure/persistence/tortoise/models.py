from enum import Enum

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


class OutboxStatusEnum(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    DONE = 'done'
    DEAD = 'dead'


class EventOutboxModel(Model):
    """事件 outbox 基类：生产模块继承后只改 `Meta.table`（表随该模块迁移）。

    事件与业务写同事务落库；relay 认领 / 重试 / 死信都写在表上。
    """
    id = fields.UUIDField(primary_key=True)
    event_type = fields.CharField(max_length=255)
    payload = fields.JSONField()
    occurred_at = fields.DatetimeField()
    status = fields.CharEnumField(
        OutboxStatusEnum, max_length=16, default=OutboxStatusEnum.PENDING)
    attempts = fields.IntField(default=0)
    next_attempt_at = fields.DatetimeField()
    locked_at = fields.DatetimeField(null=True)
    last_error = fields.TextField(null=True)
    persisted_at = fields.DatetimeField(auto_now_add=True)
    processed_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True
