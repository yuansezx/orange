"""持久化后端。

core 只通过本包的后端无关门面访问持久化；具体后端由 core.persistence.backend 动态解析。
只有本包内的实现允许 import 具体 ORM。
"""
from importlib import import_module

from app.core.infrastructure.settings import CORE_SETTINGS


def _load_backend():
    persistence = CORE_SETTINGS.persistence
    if persistence is None:
        raise RuntimeError('缺少 core.persistence 配置')
    return import_module(f'app.core.infrastructure.persistence.{persistence.backend}_backend')


async def start_persistence() -> None:
    """启动：先迁移，再初始化 ORM。"""
    backend = _load_backend()
    await backend.run_migrations()
    await backend.init()


async def stop_persistence() -> None:
    """关闭：释放持久化资源。"""
    await _load_backend().close()
