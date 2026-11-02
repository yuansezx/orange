from abc import ABC, abstractmethod
from datetime import datetime

from app.monitor.domain.audit_log.entities import AuditLog
from app.monitor.domain.audit_log.enums import AuditResultEnum
from app.monitor.domain.shared.value_objects import OperatorId


class AuditLogRepository(ABC):
    """审计日志仓储（**只追加**：不提供 update / delete）。

    查询参数只覆盖审计页的主筛选维度；`detail` 里的 JSON 不参与过滤。
    """

    @abstractmethod
    async def create(self, audit_log: AuditLog) -> AuditLog: ...

    @abstractmethod
    async def get_all(self, *,
                      module: str | None = None,
                      resource: str | None = None,
                      action: str | None = None,
                      operator_id: OperatorId | None = None,
                      target_type: str | None = None,
                      target_id: str | None = None,
                      result: AuditResultEnum | None = None,
                      request_id: str | None = None,
                      occurred_from: datetime | None = None,
                      occurred_to: datetime | None = None,
                      offset: int = 0,
                      limit: int = 50) -> list[AuditLog]: ...

    @abstractmethod
    async def count(self, *,
                    module: str | None = None,
                    resource: str | None = None,
                    action: str | None = None,
                    operator_id: OperatorId | None = None,
                    target_type: str | None = None,
                    target_id: str | None = None,
                    result: AuditResultEnum | None = None,
                    request_id: str | None = None,
                    occurred_from: datetime | None = None,
                    occurred_to: datetime | None = None) -> int: ...
