from datetime import datetime

from pydantic import BaseModel


class AuditableEntity[IdType](BaseModel):
    """带审计字段"""
    created_at: datetime
    created_by: IdType
    updated_at: datetime | None = None
    updated_by: IdType | None = None
    deleted_at: datetime | None = None
    deleted_by: IdType | None = None
