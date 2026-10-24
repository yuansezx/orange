"""会话管理适配器：JWT（自包含有效期）+ Redis 会话白名单。

键 `iam:user_sessions:{uid}` 为 hash：field=session_id（即 JWT 的 `jti`）、
value=会话元数据 JSON（login_at / expires_at / login_ip / login_user_agent）；
每个 field 用 HEXPIRE 设独立 TTL（=令牌有效期）。多端=多 field；
单端吊销 HDEL、全端吊销 DEL。服务端不保存 bearer token 本身。
（依赖 Redis ≥7.4 的 HEXPIRE）
"""
import jwt
from future_uuid import uuid7
from pydantic import ValidationError
from redis.asyncio import Redis

from app.iam.application.current_user.ports import (
    AuthenticatedSession,
    SessionInfo,
    SessionManagerPort,
    SessionMeta,
    SessionVerificationException,
)
from app.iam.domain.shared.value_objects import UserId
from app.iam.infrastructure.settings import IAM_SETTINGS


class SessionManagerJWTRedisAdapter(SessionManagerPort):
    _KEY_PREFIX = 'iam:user_sessions:'

    def __init__(self, redis_conn: Redis):
        self.redis_conn = redis_conn
        self.jwt_secret_key = IAM_SETTINGS.jwt_config.secret_key
        self.jwt_algorithm = IAM_SETTINGS.jwt_config.algorithm

    @classmethod
    def _key(cls, user_id: UserId) -> str:
        return f'{cls._KEY_PREFIX}{user_id}'

    async def create(self, user_id: UserId, ttl: int, *, meta: SessionMeta) -> str:
        session_id = str(uuid7())
        token = jwt.encode(
            {'user_id': str(user_id.value), 'jti': session_id, 'exp': meta.expires_at},
            self.jwt_secret_key,
            algorithm=self.jwt_algorithm,
        )
        key = self._key(user_id)
        await self.redis_conn.hset(key, session_id, meta.model_dump_json())
        await self.redis_conn.hexpire(key, ttl, session_id)
        return token

    async def authenticate(self, token: str) -> AuthenticatedSession:
        try:
            # jwt.decode 默认校验 signature + exp
            payload = jwt.decode(token, self.jwt_secret_key, [self.jwt_algorithm])
        except jwt.exceptions.InvalidTokenError:
            raise SessionVerificationException('无效 token')
        user_id = UserId(payload['user_id'])
        session_id = payload.get('jti')
        if not session_id or not await self.redis_conn.hexists(self._key(user_id), session_id):
            raise SessionVerificationException('会话已失效')
        return AuthenticatedSession(user_id=user_id, session_id=session_id)

    async def get_all(self, user_id: UserId | None = None) -> list[SessionInfo]:
        if user_id is not None:
            return await self._read_user_sessions(user_id)
        sessions: list[SessionInfo] = []
        async for key in self.redis_conn.scan_iter(match=f'{self._KEY_PREFIX}*'):
            uid = UserId(key.removeprefix(self._KEY_PREFIX))
            sessions.extend(await self._read_user_sessions(uid))
        return sessions

    async def _read_user_sessions(self, user_id: UserId) -> list[SessionInfo]:
        raw = await self.redis_conn.hgetall(self._key(user_id))
        sessions: list[SessionInfo] = []
        for session_id, value in raw.items():
            try:
                meta = SessionMeta.model_validate_json(value)
            except ValidationError:
                continue  # 旧占位值 '1' 或损坏数据
            sessions.append(
                SessionInfo(user_id=user_id, session_id=session_id, **meta.model_dump()))
        return sessions

    async def revoke(self, user_id: UserId, session_id: str) -> bool:
        return bool(await self.redis_conn.hdel(self._key(user_id), session_id))

    async def revoke_all(self, user_id: UserId) -> None:
        await self.redis_conn.delete(self._key(user_id))
