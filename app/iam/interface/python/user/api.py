"""用户生命周期事件的公开订阅 API。

消费方（其他模块）在 bootstrap / 组合根调用；回调收到裸 UUID——
事件类型与值对象不跨模块（遵循「跨模块 ID 一律传裸值」约定）。
"""
from typing import Awaitable, Callable, cast
from uuid import UUID

from app.core import get_event_bus
from app.core.domain.event_bus import EventHandler
from app.core.domain.events import BaseEvent
from app.iam.domain.user.events import UserHardDeleted

UserHardDeletedCallback = Callable[[UUID], Awaitable[None]]


class _UserHardDeletedCallbackHandler(EventHandler):

    def __init__(self, callback: UserHardDeletedCallback) -> None:
        self._callback = callback

    async def handle(self, event: BaseEvent) -> None:
        # 总线按事件类型订阅，这里只会收到 UserHardDeleted
        await self._callback(cast(UserHardDeleted, event).user_id.value)


def register_user_hard_deleted_listener(callback: UserHardDeletedCallback) -> None:
    """订阅「用户被彻底删除」事实。回调在业务事务提交后异步执行（当前总线 best-effort）。"""
    get_event_bus().subscribe(UserHardDeleted, _UserHardDeletedCallbackHandler(callback))
