"""用户公开 API：批量展示引用 + 生命周期事件订阅。

跨模块只传裸 UUID（事件类型与值对象不跨模块）。
"""
from typing import Awaitable, Callable, cast
from uuid import UUID

from app.core import get_event_bus
from app.core.domain.event_bus import EventHandler
from app.core.domain.events import BaseEvent
from app.iam.domain.shared.value_objects import UserId
from app.iam.domain.user.events import UserHardDeleted
from app.iam.interface.common.avatar_url import build_avatar_url
from app.iam.interface.dependences import get_user_repo
from app.iam.interface.python.user.schemas import UserRefResp

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


async def get_user_refs(user_ids: list[UUID]) -> list[UserRefResp]:
    """批量按 id 取用户展示引用；含软删用户，硬删用户自然缺失。"""
    if not user_ids:
        return []
    users = await get_user_repo().get_by_ids(
        [UserId(user_id) for user_id in user_ids], include_deleted=True)
    return [
        UserRefResp(
            id=user.id.value,
            username=user.username,
            nickname=user.nickname,
            avatar_url=build_avatar_url(user.id, user.avatar_key),
        )
        for user in users
    ]
