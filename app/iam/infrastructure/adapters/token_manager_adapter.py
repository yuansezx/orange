"""令牌管理适配器：JWT（自包含有效期）+ Redis 白名单（吊销）。

白名单键 `iam:user_tokens:{uid}` 为 hash：field=token、value=占位 `'1'`，
每个 field 用 HEXPIRE 设独立 TTL（=令牌有效期）。多端=多 field；
单端登出 HDEL、全端登出 DEL。（依赖 Redis ≥7.4 的 HEXPIRE）
"""
from datetime import datetime, timedelta, UTC

import jwt
from redis.asyncio import Redis

from app.iam.application.current_user.ports import TokenManagerPort, TokenVerificationException
from app.iam.domain.shared.value_objects import UserId
from app.iam.infrastructure.settings import IAM_SETTINGS


class TokenManagerJWTRedisAdapter(TokenManagerPort):
    def __init__(self, redis_conn: Redis):
        self.redis_conn = redis_conn
        self.jwt_secret_key = IAM_SETTINGS.jwt_config.secret_key
        self.jwt_algorithm = IAM_SETTINGS.jwt_config.algorithm

    @staticmethod
    def _key(user_id: UserId) -> str:
        return f'iam:user_tokens:{user_id}'

    async def create(self, user_id: UserId, ttl: int) -> str:
        token = jwt.encode(
            {'user_id': str(user_id.value), 'exp': datetime.now(UTC) + timedelta(seconds=ttl)},
            self.jwt_secret_key,
            algorithm=self.jwt_algorithm,
        )
        key = self._key(user_id)
        await self.redis_conn.hset(key, token, '1')
        await self.redis_conn.hexpire(key, ttl, token)
        return token

    async def authenticate(self, token: str) -> UserId:
        try:
            # jwt.decode 默认校验 signature + exp
            payload = jwt.decode(token, self.jwt_secret_key, [self.jwt_algorithm])
        except jwt.exceptions.InvalidTokenError:
            raise TokenVerificationException('无效 token')
        user_id = UserId(value=payload['user_id'])
        if not await self.redis_conn.hexists(self._key(user_id), token):
            raise TokenVerificationException('token 已失效')
        return user_id

    async def revoke(self, token: str) -> None:
        try:
            # 仍验签名，但不校验 exp（过期令牌也允许登出清理）
            payload = jwt.decode(token, self.jwt_secret_key, [self.jwt_algorithm],
                                 options={'verify_exp': False})
        except jwt.exceptions.InvalidTokenError:
            raise TokenVerificationException('无效 token')
        user_id = UserId(value=payload['user_id'])
        await self.redis_conn.hdel(self._key(user_id), token)

    async def revoke_all(self, user_id: UserId) -> None:
        await self.redis_conn.delete(self._key(user_id))
