from dataclasses import dataclass

from app.core.domain.value_objects import BaseEntityId


@dataclass(frozen=True)
class AuditLogId(BaseEntityId):
    pass


@dataclass(frozen=True)
class OperatorId(BaseEntityId):
    """审计记录的操作人 id（跨模块快照）。

    不直接引用 iam 的 `UserId`：audit 是通用监控能力，不依赖具体身份模块的类型。
    """
