from aerich import Command
from loguru import logger
from tortoise import Tortoise
from tortoise.transactions import in_transaction

from app.core.domain.units_of_work import InTransactionType, TransactionContext
from app.core.infrastructure.settings import CORE_SETTINGS

MIGRATIONS_DIR = './migrations'


def _build_apps() -> dict:
    """按约定 app.{模块}.infrastructure.persistence.{后端}.models 汇总各模块的模型。

    aerich.models（迁移追踪表）在每个模块里都列一份：tortoise 内部按 _meta.app 去重，
    只会归给第一个认领它的 label，因此重复列是安全的。
    """
    backend = CORE_SETTINGS.persistence.backend
    return {
        m: {
            'models': [f'app.{m}.infrastructure.persistence.{backend}.models', 'aerich.models'],
            'default_connection': 'default',
        }
        for m in CORE_SETTINGS.modules
    }


def build_tortoise_config() -> dict:
    """把 core 配置装配成 tortoise 认的完整配置（运行时与 aerich 共用同一份）。"""
    config = dict(CORE_SETTINGS.persistence.options)
    config['apps'] = _build_apps()
    return config


async def init() -> None:
    # _enable_global_fallback：lifespan 与请求不在同一个 task，需开全局上下文回退
    await Tortoise.init(config=build_tortoise_config(), _enable_global_fallback=True)
    logger.info('ORM 初始化完成')


async def close() -> None:
    await Tortoise.close_connections()


async def run_migrations() -> None:
    """启动前按 app label 逐个执行迁移（dev：自动 detect → 生成 → 应用）。"""
    config = build_tortoise_config()
    for app_label in config['apps']:
        command = Command(tortoise_config=config, app=app_label, location=MIGRATIONS_DIR)
        try:
            try:
                await command.init_db(safe=True)
                logger.info('[{}] 数据库表初始化完成', app_label)
            except FileExistsError:
                await command.init()
                new_migration = await command.migrate(name='auto', no_input=True)
                if new_migration:
                    logger.info('[{}] 生成迁移脚本 {}', app_label, new_migration)
                migrated = await command.upgrade()
                for version in migrated:
                    logger.info('[{}] 应用迁移 {}', app_label, version)
                if not migrated:
                    logger.info('[{}] 数据库表已是最新', app_label)
        finally:
            await command.aclose()


class TortoiseTransactionContext(TransactionContext):
    """把 tortoise 的 in_transaction() 适配成领域侧的事务上下文。

    tortoise 的事务连接按 task 的 ContextVar 自动绑定，事务内的查询无需显式传连接。
    """

    def __init__(self) -> None:
        self._cm = None

    async def __aenter__(self):
        # 进入时才创建，避免在构造期触碰连接/上下文
        self._cm = in_transaction()
        return await self._cm.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._cm.__aexit__(exc_type, exc_val, exc_tb)


# 后端提供的事务工厂（InTransactionType = Callable[[], TransactionContext]）
IN_TRANSACTION: InTransactionType = TortoiseTransactionContext
