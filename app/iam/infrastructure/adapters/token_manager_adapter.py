import jwt
from redis import asyncio as aioredis

from app.iam.application.common.exceptions import InvalidTokenException
from app.iam.application.current_user.ports import TokenManagerPort
from app.iam.domain.shared.value_objects import UserId
from app.iam.infrastructure.settings import IAM_SETTINGS


class TokenManagerJWTRedisAdapter(TokenManagerPort):
    def __init__(self,redis_conn:aioredis.Redis):
        self.redis_conn = redis_conn
        self.jwt_secret_key=IAM_SETTINGS.jwt_config.secret_key
        self.jwt_algorithm=IAM_SETTINGS.jwt_config.algorithm

    def authenticate(self, token:str) -> UserId:
        try:
            payload = jwt.decode(token, self.jwt_secret_key, [self.jwt_algorithm])
        except jwt.exceptions.InvalidTokenError:
            raise InvalidTokenException('无效token')
        return UserId(value=payload['user_id'])

