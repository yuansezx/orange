"""API Key 仓储的 Redis cache-aside 装饰器。

缓存只服务认证路径（`get_by_token_hash`）；写路径负责淘汰，TTL 兜底。
`last_used_at` 不进缓存：每次 cache miss（装载）时若 key 可认证则写一次库，
使用时间的刷新频率因此与 TTL 一致。
不缓存按 key 派生的 CurrentUser——那是用户快照，按 user_id 单独缓存。
"""
from datetime import datetime, UTC

from loguru import logger
from redis.asyncio import Redis

from app.core.exceptions import PersistenceException
from app.iam.domain.api_key.entities import ApiKey
from app.iam.domain.api_key.repositories import ApiKeyRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import ApiKeyId, UserId

API_KEY_CACHE_TTL_SECONDS = 3600


class ApiKeyRepositoryWithRedisCacheImpl(ApiKeyRepository):

    def __init__(self, *, inner: ApiKeyRepository, redis_conn: Redis) -> None:
        self.inner = inner
        self.redis_conn = redis_conn

    @staticmethod
    def _key(token_hash: str) -> str:
        return f'iam:api_key:{token_hash}'

    # ---------------- 认证路径（cache-aside） ----------------

    async def get_by_token_hash(self, token_hash: str, *,
                                include_deleted: bool = False) -> ApiKey | None:
        if include_deleted:  # 回收站/唯一性场景不走缓存
            return await self.inner.get_by_token_hash(token_hash, include_deleted=True)

        cache_key = self._key(token_hash)
        raw = await self.redis_conn.get(cache_key)
        if raw:
            return ApiKey.model_validate_json(raw)

        key = await self.inner.get_by_token_hash(token_hash)
        if key is not None:
            now = datetime.now(UTC)
            if key.can_authenticate(now):
                # 每个装载窗口记一次使用；缓存不存 last_used_at，下次 miss 再刷新
                try:
                    await self.inner.update_last_used(key.id, now)
                except PersistenceException:
                    logger.exception('更新 API Key 最近使用时间失败：api_key_id={}', key.id)
            await self.redis_conn.set(
                cache_key,
                key.model_dump_json(exclude={'last_used_at'}),
                ex=API_KEY_CACHE_TTL_SECONDS,
            )
        return key

    # ---------------- 写路径（落库后淘汰） ----------------

    async def create(self, entity: ApiKey) -> ApiKey:
        created = await self.inner.create(entity)
        await self._evict(created)
        return created

    async def bulk_create(self, entities: list[ApiKey]) -> list[ApiKey]:
        created = await self.inner.bulk_create(entities)
        for entity in created:
            await self._evict(entity)
        return created

    async def update(self, entity: ApiKey) -> ApiKey:
        updated = await self.inner.update(entity)
        await self._evict(updated)
        return updated

    async def hard_delete(self, entity_ids: ApiKeyId | list[ApiKeyId]) -> int:
        ids = entity_ids if isinstance(entity_ids, list) else [entity_ids]
        keys: list[ApiKey] = []
        for key_id in ids:
            key = await self.inner.get(key_id, include_deleted=True)
            if key is not None:
                keys.append(key)
        deleted = await self.inner.hard_delete(entity_ids)
        for key in keys:
            await self._evict(key)
        return deleted

    async def hard_delete_by_user(self, user_id: UserId) -> int:
        keys = await self.inner.get_all(user_id=user_id, deleted=False)
        keys += await self.inner.get_all(user_id=user_id, deleted=True)
        deleted = await self.inner.hard_delete_by_user(user_id)
        for key in keys:
            await self._evict(key)
        return deleted

    # ---------------- 管理读/写（直接委托） ----------------

    async def get(self, entity_id: ApiKeyId, *,
                  include_deleted: bool = False) -> ApiKey | None:
        return await self.inner.get(entity_id, include_deleted=include_deleted)

    async def get_all(self, user_id: UserId | None = None, status: StatusEnum | None = None,
                      deleted: bool = False) -> list[ApiKey]:
        return await self.inner.get_all(user_id=user_id, status=status, deleted=deleted)

    async def update_last_used(self, api_key_id: ApiKeyId, used_at: datetime) -> None:
        # 不碰缓存：last_used 只影响节流频率，旧值无害
        await self.inner.update_last_used(api_key_id, used_at)

    async def _evict(self, key: ApiKey) -> None:
        await self.redis_conn.delete(self._key(key.token_hash))
