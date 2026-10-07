"""持久化后端。

core 只通过本包的后端无关门面访问持久化；具体后端由 core.persistence.backend 动态解析。
只有本包内的实现允许 import 具体 ORM。
"""
from importlib import import_module

from loguru import logger

from app.core.domain.units_of_work import InTransactionType
from app.core.infrastructure.settings import CORE_SETTINGS


def _load_backend():
    persistence = CORE_SETTINGS.persistence
    if persistence is None:
        raise RuntimeError('缺少 core.persistence 配置')
    return import_module(f'app.core.infrastructure.persistence.{persistence.backend}.{persistence.backend}_backend')


async def start_persistence() -> None:
    """启动：按开关决定是否迁移，然后初始化 ORM。"""
    backend = _load_backend()
    if CORE_SETTINGS.persistence.auto_migrate:
        await backend.run_migrations()
    else:
        logger.info('auto_migrate 已关闭，跳过启动期迁移（可运行 python -m scripts.migrate 手动迁移）')
    await backend.init()


async def stop_persistence() -> None:
    """关闭：释放持久化资源。"""
    await _load_backend().close()


async def run_persistence_migrations() -> None:
    """手动触发一次迁移（auto_migrate 关闭、或需单独迁移时用）。"""
    await _load_backend().run_migrations()


def get_in_transaction() -> InTransactionType:
    """事务上下文工厂（由后端提供），供应用层注入使用。"""
    return _load_backend().IN_TRANSACTION


def module_infra(module: str, sub: str):
    """按约定导入某模块的方言基础设施子模块（models / repositories / queries）。

    组合根用它取方言实现而不硬编码方言（方言由模块的连接决定）。
    """
    return _load_backend().infra_module(module, sub)
