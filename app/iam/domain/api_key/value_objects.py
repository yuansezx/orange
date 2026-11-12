import secrets
from typing import Self

from pydantic import field_validator

from app.core.domain.value_objects import SingleValueObject
from app.core.utils.secret_hash import hash_secret
from app.iam.domain.api_key.exceptions import InvalidApiKeyTokenException

TOKEN_PREFIX = 'orange_ak_'
TOKEN_BYTES = 32
_MIN_TOKEN_LENGTH = len(TOKEN_PREFIX) + 32


class ApiKeyToken(SingleValueObject[str]):
    """API Key 明文凭据（只在创建响应中出现一次，不落库、不进日志）。

    实体只存 `digest`（SHA-256）与 `masked`（展示掩码）；
    `str()` 返回掩码，取明文用 `.value`。
    """

    @field_validator('root')
    @classmethod
    def _validate(cls, value: str) -> str:
        if not value.startswith(TOKEN_PREFIX) or len(value) < _MIN_TOKEN_LENGTH:
            raise InvalidApiKeyTokenException('API Key 令牌格式非法')
        return value

    @classmethod
    def generate(cls) -> Self:
        return cls(TOKEN_PREFIX + secrets.token_urlsafe(TOKEN_BYTES))

    @staticmethod
    def is_api_key_token(value: str) -> bool:
        """只看前缀，供统一认证入口确定性路由（不校验完整格式）。"""
        return value.startswith(TOKEN_PREFIX)

    @property
    def digest(self) -> str:
        return hash_secret(self.root)

    @property
    def masked(self) -> str:
        return f'{TOKEN_PREFIX}••••{self.root[-4:]}'

    def __str__(self) -> str:
        return self.masked
