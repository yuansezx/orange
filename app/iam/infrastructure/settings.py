import secrets

from loguru import logger
from pydantic import BaseModel, field_validator
from pydantic_settings import SettingsConfigDict

from app.core.infrastructure.settings import AppBaseSettings


class JWTConfig(BaseModel):
    # 允许留空：启动时生成临时密钥，重启即失效（所有会话需重新登录）
    secret_key: str | None = None
    algorithm: str = 'HS256'
    expire_minutes: int = 30

    @field_validator('secret_key')
    @classmethod
    def _generate_secret_if_missing(cls, value: str | None) -> str:
        if value:
            return value
        logger.warning('iam.jwt_config.secret_key 未配置，已生成临时密钥；重启后所有会话失效')
        return secrets.token_hex(32)


class CurrentUserConfig(BaseModel):
    # CurrentUser 快照缓存 TTL（秒）；缺省 = 令牌期（jwt_config.expire_minutes × 60）
    snapshot_ttl_seconds: int | None = None


class AvatarStorageConfig(BaseModel):
    """头像存储：引用 core.object_storage 的哪条连接；桶名由 adapter 代码拥有。"""
    connection: str = 'default'


class IAMSettings(AppBaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=['config_dev.yaml', 'config.yaml', 'config_prod.yaml'],
        yaml_config_section='iam',
        yaml_file_encoding='utf-8',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    jwt_config: JWTConfig | None = None
    current_user_config: CurrentUserConfig = CurrentUserConfig()
    # 未配置 = 不启用头像存储（个人资料仍可用，只是没有头像）
    avatar_storage: AvatarStorageConfig | None = None

    def __init__(self):
        super().__init__()
        if not self.jwt_config:
            # 未配置 jwt_config：用默认算法，secret_key 由 JWTConfig 生成临时值
            self.jwt_config = JWTConfig()
        # 快照 TTL 未显式配置时对齐令牌期：快照无需比会话更长寿（超期即静默重解析）
        if self.current_user_config.snapshot_ttl_seconds is None:
            self.current_user_config.snapshot_ttl_seconds = self.jwt_config.expire_minutes * 60


IAM_SETTINGS = IAMSettings()
