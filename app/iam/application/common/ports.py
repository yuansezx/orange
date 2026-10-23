from abc import ABC, abstractmethod
from typing import Any

from app.core.application.dto import RequestMeta
from app.iam.domain.current_user.entities import CurrentUser


class AuditLogWriterPort(ABC):
    """审计日志写入端口（参数用调用方语言：操作人 + 请求上下文 + 业务事件）。

    业务数据变更场景：调用方在业务事务内调用，保证审计与业务原子提交。
    无业务事务场景（如登录失败）：调用方自行开事务后调用。
    """

    @abstractmethod
    async def write(self, *,
                    resource: str, action: str, summary: str,
                    current_user: CurrentUser | None = None,
                    request_meta: RequestMeta | None = None,
                    target_type: str | None = None,
                    target_id: str | None = None,
                    target_name: str | None = None,
                    detail: dict[str, Any] | None = None) -> None: ...
