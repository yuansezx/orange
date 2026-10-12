import secrets

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict

from app.core.infrastructure.settings import AppBaseSettings


class JWTConfig(BaseModel):
    secret_key: str
    algorithm: str
    expire_minutes: int = 30


class CurrentUserConfig(BaseModel):
    # CurrentUser 快照缓存 TTL（秒）；缺省 = 令牌期（jwt_config.expire_minutes × 60）
    snapshot_ttl_seconds: int | None = None


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

    def __init__(self):
        super().__init__()
        if not self.jwt_config:
            # 默认随机secret_key
            self.jwt_config = JWTConfig(secret_key=secrets.token_hex(32), algorithm='HS256')
        # 快照 TTL 未显式配置时对齐令牌期：快照无需比会话更长寿（超期即静默重解析）
        if self.current_user_config.snapshot_ttl_seconds is None:
            self.current_user_config.snapshot_ttl_seconds = self.jwt_config.expire_minutes * 60


IAM_SETTINGS = IAMSettings()
