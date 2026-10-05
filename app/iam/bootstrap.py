"""iam 模块的启动钩子。

由 core 按 `core.modules` 约定动态 import 并调用（见 app/core/__init__.py 的
_run_module_bootstraps）。放独立模块而非 `__init__.py`，是为了避免 import 副作用
（任何 `import app.iam.*` 都会执行包 `__init__`）。
"""
from loguru import logger

from app.iam.domain.user.entities import SUPER_ADMIN_USERNAME
from app.iam.interface.dependences import get_user_app_service

# 超管账户硬编码（不读配置）：用户名取自领域常量 SUPER_ADMIN_USERNAME（'admin'，保留名）
# 初始密码首次登录强制修改
SUPER_ADMIN_INITIAL_PASSWORD = 'admin123'


async def bootstrap() -> None:
    """初始化首个超管（逃生舱）。库里已有超管则跳过。"""
    logger.info('初始化超管账户 {!r}（若不存在）', SUPER_ADMIN_USERNAME)
    await get_user_app_service().initialize_super_admin(
        username=SUPER_ADMIN_USERNAME,
        password=SUPER_ADMIN_INITIAL_PASSWORD,
        nickname=SUPER_ADMIN_USERNAME,
    )
