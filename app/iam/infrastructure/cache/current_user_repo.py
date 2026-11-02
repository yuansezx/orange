"""CurrentUser 缓存（Redis）实现。

键 `iam:current_user:{uid}` = CurrentUser JSON，带独立短 TTL。
权限/角色变更只需清此快照，会话（令牌白名单）不受影响。
"""
from __future__ import annotations  # 方法名 set 会遮蔽内建 set，注解须延迟求值

from redis.asyncio import Redis

from app.core.utils.type_utils import to_set
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.current_user.repositories import CurrentUserRepository
from app.iam.domain.shared.value_objects import UserId
from app.iam.infrastructure.settings import IAM_SETTINGS


class CurrentUserRepositoryRedisImpl(CurrentUserRepository):

    def __init__(self, redis_conn: Redis):
        self.redis_conn = redis_conn
        self._ttl = IAM_SETTINGS.current_user_config.snapshot_ttl_seconds

    @staticmethod
    def _key(user_id: UserId) -> str:
        return f'iam:current_user:{user_id}'

    async def set(self, current_user: CurrentUser) -> None:
        await self.redis_conn.set(
            self._key(current_user.user_id), current_user.model_dump_json(), ex=self._ttl)

    async def get(self, user_id: UserId) -> CurrentUser | None:
        raw = await self.redis_conn.get(self._key(user_id))
        return CurrentUser.model_validate_json(raw) if raw else None

    async def evict(self, user_ids: UserId | list[UserId] | set[UserId]) -> None:
        ids = to_set(user_ids)
        if ids:
            await self.redis_conn.delete(*[self._key(u) for u in ids])
