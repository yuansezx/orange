"""手动迁移入口：`uv run python -m scripts.migrate`

与启动期迁移共用同一套逻辑（run_migrations），供 auto_migrate 关闭时使用。
"""
import asyncio

from app.core import init_logger
from app.core.infrastructure.persistence import run_persistence_migrations


if __name__ == '__main__':
    init_logger()
    asyncio.run(run_persistence_migrations())
