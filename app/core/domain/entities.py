from datetime import datetime

from pydantic import BaseModel


class AuditableEntity[IdType](BaseModel):
    """带审计字段。

    删除是与业务状态**正交**的独立维度：`deleted_at` 是否为空是删除的唯一判别，
    业务状态字段（如 status）只表达可用性。`is_deleted` 是派生视图，不落库、不重复存储。
    """
    created_at: datetime
    created_by: IdType
    updated_at: datetime | None = None
    updated_by: IdType | None = None
    deleted_at: datetime | None = None
    deleted_by: IdType | None = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
