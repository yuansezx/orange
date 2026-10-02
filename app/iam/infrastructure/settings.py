import secrets

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict

from app.core.infrastructure.settings import AppBaseSettings


class JWTConfig(BaseModel):
    secret_key: str
    algorithm: str

class IAMSettings(AppBaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=['config_dev.yaml', 'config.yaml', 'config_prod.yaml'],
        yaml_config_section='iam',
        yaml_file_encoding='utf-8',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    jwt_config : JWTConfig | None = None

    def __init__(self):
        super().__init__()
        if not self.jwt_config:
            # 默认随机secret_key
            self.jwt_config = JWTConfig(secret_key=secrets.token_hex(32), algorithm='HS256')

IAM_SETTINGS = IAMSettings()