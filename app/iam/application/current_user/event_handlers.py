"""CurrentUser 快照的缓存失效订阅者。

快照含 user / roles / permission_codes，任一侧变动都要重解析：用户级事件直接清该用户；
角色级事件需反查持有该角色的用户（扇出）。清缓存幂等、多清无害，故异常只记日志、
不让其冒到事件总线。
"""
from loguru import logger

from app.core.domain.event_bus import EventHandler
from app.core.domain.events import BaseEvent
from app.iam.domain.current_user.repositories import CurrentUserRepository
from app.iam.domain.role.events import RoleChanged
from app.iam.domain.shared.value_objects import UserId
from app.iam.domain.user.events import UserChanged
from app.iam.domain.user_role_assignment.events import UserRolesChanged
from app.iam.domain.user_role_assignment.repositories import UserRoleRepository


class CurrentUserCacheInvalidationHandler(EventHandler):
    def __init__(self, current_user_repo: CurrentUserRepository, user_role_repo: UserRoleRepository):
        self.current_user_repo = current_user_repo
        self.user_role_repo = user_role_repo

    async def handle(self, event: BaseEvent) -> None:
        try:
            user_ids = await self._affected_users(event)
            if user_ids:
                await self.current_user_repo.evict(user_ids)
        except Exception as e:
            logger.error('清 CurrentUser 快照失败：{}', e)

    async def _affected_users(self, event: BaseEvent) -> set[UserId] | None:
        if isinstance(event, (UserChanged, UserRolesChanged)):
            return {event.user_id}
        if isinstance(event, RoleChanged):
            return set(await self.user_role_repo.get_user_ids_by_role(event.role_id))
        return None
