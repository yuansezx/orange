# 全局配置,包括数据库配置,jwt配置
# import secrets
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, YamlConfigSettingsSource


class AppBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=['config_dev.yaml', 'config.yaml', 'config_prod.yaml'],
        yaml_file_encoding='utf-8',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # hook,配置 '配置源' 及其优先级
    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        yaml_settings = YamlConfigSettingsSource(settings_cls)
        # 优先级（靠前更高）：显式参数 > 进程环境变量 > .env > YAML > secrets
        # 关键：env 高于 yaml，容器里才能用环境变量覆盖配置文件
        return init_settings, env_settings, dotenv_settings, yaml_settings, file_secret_settings


class PersistenceConfig(BaseModel):
    """持久化配置（core 段内的嵌套 schema）。

    backend：选择 ORM 后端（对应 persistence/{backend}/{backend}_backend.py）；
    auto_migrate：启动时是否自动执行迁移；关闭则跳过，改为手动触发（migrate.py）；
    use_tz / timezone：tortoise 时区配置；
    options：连接映射 {连接名: {dialect, credentials}}。每个连接**自带引擎** dialect
             （对应 persistence/{backend}/{dialect}/），故不同连接可用不同引擎。
    """
    backend: str
    auto_migrate: bool = True
    use_tz: bool = True
    timezone: str = 'Asia/Shanghai'
    options: dict = {}


class CacheConfig(BaseModel):
    """缓存配置（core 段内的嵌套 schema）。

    backend：选择缓存后端（对应 cache/{backend}/{backend}_backend.py）；
    options：后端专属配置，core 原样透传、不解释（如 redis 的 host/port/password/db）。
    未配置则 core 不启动缓存。
    """
    backend: str = 'redis'
    options: dict = {}


class CoreSettings(AppBaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=['config_dev.yaml', 'config.yaml', 'config_prod.yaml'],
        yaml_config_section='core',
        yaml_file_encoding='utf-8',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    app_name: str = 'orange'
    app_version: str = 'nightly'
    debug: bool = False

    # 服务监听地址（容器内需绑 0.0.0.0）
    host: str = '127.0.0.1'
    port: int = 8500
    # # docs url
    # docs_url : str = None
    # redoc_url : str = None
    #
    # # cors
    # cors_allowed_origins : list[str] | None = None
    #
    # # jwt配置
    # jwt_secret_key: str | None = None
    # jwt_algorithm: str = 'HS256'
    # jwt_token_expire_minutes: int = 30
    #
    # # 是否需要初始化数据库
    # need_init_db: bool = True
    #
    # log文件位置
    logs_dir: Path = Path('./logs')

    # 启用的业务模块（core 按约定汇总各模块的模型/路由等装配）
    modules: list[str] = []

    # 持久化（数据库）配置
    persistence: PersistenceConfig | None = None

    # 缓存配置（可选；未配置则 core 不启动缓存，用到时才报错）
    cache: CacheConfig | None = None

    # def __init__(self):
    #     super().__init__()
    #     # orm默认配置
    #     if not self.tortoise_orm_config:
    #         self.tortoise_orm_config = {
    #             'connections': {
    #                 'default': 'sqlite://db.sqlite3'
    #             },
    #             'apps': {
    #                 'models': {
    #                     'models': ['app.user.models', 'aerich.models'],
    #                     'default_connection': 'default',
    #                 }
    #             },
    #             'use_tz': True,  # 是否使用时区
    #             'timezone': 'Asia/Shanghai',  # 默认时区
    #             'db_pool': {
    #                 'max_size': 10,
    #                 'min_size': 1,
    #                 'idle_timeout': 30  # 空闲连接超时
    #             }
    #         }
    #     # redis_key_ex默认配置
    #     if self.redis_key_token_ex is None:
    #         self.redis_key_token_ex = self.jwt_token_expire_minutes * 60
    #     # jwt默认配置
    #     if self.jwt_secret_key is None:
    #         self.jwt_secret_key = secrets.token_hex(32)


CORE_SETTINGS = CoreSettings()
