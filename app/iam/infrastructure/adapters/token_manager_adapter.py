"""令牌管理适配器：JWT（自包含有效期）+ Redis 会话白名单（吊销）。

键 `iam:user_sessions:{uid}` 为 hash：field=jti、value=占位 `'1'`
（后续可放登录时间/IP/UA 等元数据）；每个 field 用 HEXPIRE 设独立 TTL
（=令牌有效期）。多端=多 field；单端登出 HDEL、全端登出 DEL。
Server 不保存 bearer token 本身，只保存会话 jti。（依赖 Redis ≥7.4 的 HEXPIRE）
"""
from datetime import datetime, timedelta, UTC

import jwt
from future_uuid import uuid7
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
        return f'iam:user_sessions:{user_id}'

    async def create(self, user_id: UserId, ttl: int) -> str:
        jti = str(uuid7())
        token = jwt.encode(
            {'user_id': str(user_id.value), 'jti': jti,
             'exp': datetime.now(UTC) + timedelta(seconds=ttl)},
            self.jwt_secret_key,
            algorithm=self.jwt_algorithm,
        )
        key = self._key(user_id)
        await self.redis_conn.hset(key, jti, '1')
        await self.redis_conn.hexpire(key, ttl, jti)
        return token

    async def authenticate(self, token: str) -> UserId:
        try:
            # jwt.decode 默认校验 signature + exp
            payload = jwt.decode(token, self.jwt_secret_key, [self.jwt_algorithm])
        except jwt.exceptions.InvalidTokenError:
            raise TokenVerificationException('无效 token')
        user_id = UserId(payload['user_id'])
        jti = payload.get('jti')
        if not jti or not await self.redis_conn.hexists(self._key(user_id), jti):
            raise TokenVerificationException('token 已失效')
        return user_id

    async def revoke(self, token: str) -> None:
        try:
            # 仍验签名，但不校验 exp（过期令牌也允许登出清理）
            payload = jwt.decode(token, self.jwt_secret_key, [self.jwt_algorithm],
                                 options={'verify_exp': False})
        except jwt.exceptions.InvalidTokenError:
            raise TokenVerificationException('无效 token')
        user_id = UserId(payload['user_id'])
        jti = payload.get('jti')
        if not jti:
            raise TokenVerificationException('无效 token')
        await self.redis_conn.hdel(self._key(user_id), jti)

    async def revoke_all(self, user_id: UserId) -> None:
        await self.redis_conn.delete(self._key(user_id))
