"""资源/权限目录注册的公开 Python API。

各模块在自己的 `bootstrap.py` 里调用 `register_module_resources`，把本模块的
`SYSTEM` 资源声明幂等注册到 iam 的目录中。
"""
from loguru import logger

from app.iam.application.resource.dto import RegisterPermissionIn, RegisterResourceIn
from app.iam.domain.user.entities import SUPER_ADMIN_USERNAME
from app.iam.interface.dependences import get_resource_app_service, get_user_repo

__all__ = ['RegisterPermissionIn', 'RegisterResourceIn', 'register_module_resources']


async def register_module_resources(module: str,
                                    declarations: list[RegisterResourceIn]) -> None:
    """以超管为操作人，幂等注册某模块的资源/权限声明并执行对账。"""
    operator_id = await get_user_repo().get_id_by_username(SUPER_ADMIN_USERNAME)
    if operator_id is None:
        logger.warning('未找到超管 id，跳过模块 {!r} 的资源/权限目录注册', module)
        return
    await get_resource_app_service().register_resources(module, declarations, operator_id)
