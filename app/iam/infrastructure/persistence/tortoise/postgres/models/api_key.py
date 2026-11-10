from future_uuid import uuid7
from tortoise import fields
from tortoise.contrib.postgres import fields as postgres_fields

from app.core.infrastructure.persistence.tortoise.models import AuditableModel
from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum


class ApiKeyModel(AuditableModel):
    """API Key（用户凭据 / PAT）的表模型。"""

    id = fields.UUIDField(primary_key=True, default=uuid7)
    user_id = fields.UUIDField(db_index=True)
    name = fields.CharField(max_length=64)
    # 整串 token 的 SHA-256；唯一索引就是认证查找路径
    token_hash = fields.CharField(max_length=64, unique=True)
    token_masked = fields.CharField(max_length=64)
    scopes = postgres_fields.ArrayField('varchar', default=list)
    data_scope_kind = fields.CharEnumField(DataScopeEnum, max_length=50)
    data_scope_dept_ids = postgres_fields.ArrayField('uuid', default=list)
    status = fields.CharEnumField(StatusEnum, max_length=50)
    expires_at = fields.DatetimeField(null=True)
    last_used_at = fields.DatetimeField(null=True)

    class Meta:
        table = 'iam_api_key'
