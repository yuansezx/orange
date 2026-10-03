from future_uuid import uuid7
from tortoise import fields

from app.core.infrastructure.persistence.tortoise.models import AuditableModel
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.user.enums import UserTypeEnum


class UserModel(AuditableModel):
    """user 聚合的表模型（与领域实体 app.iam.domain.user.entities.User 分离）。"""

    id = fields.UUIDField(primary_key=True, default=uuid7)
    username = fields.CharField(max_length=64, unique=True)
    nickname = fields.CharField(max_length=64)
    password_hash = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, null=True, unique=True)
    phone = fields.CharField(max_length=20, null=True, unique=True)
    user_type = fields.CharEnumField(UserTypeEnum, max_length=32)
    status = fields.CharEnumField(StatusEnum, max_length=16)
    need_change_password = fields.BooleanField(default=True)
    password_updated_at = fields.DatetimeField(null=True)
    remark = fields.CharField(max_length=255, null=True)
    dept_id = fields.UUIDField(null=True)

    class Meta:
        table = 'iam_user'
