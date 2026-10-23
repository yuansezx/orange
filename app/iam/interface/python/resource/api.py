"""资源/权限目录注册的公开 Python API。"""
from loguru import logger

from app.iam.domain.user.entities import SUPER_ADMIN_USERNAME
from app.iam.interface.dependences import get_resource_app_service, get_user_repo
from app.iam.interface.python.resource.schemas import RegisterResourceReq


async def register_module_resources(module: str,
                                    declarations: list[RegisterResourceReq]) -> None:
    """以超管为操作人，幂等注册某模块的资源/权限声明并执行对账。"""
    operator_id = await get_user_repo().get_id_by_username(SUPER_ADMIN_USERNAME)
    if operator_id is None:
        logger.warning('未找到超管 id，跳过模块 {!r} 的资源/权限目录注册', module)
        return
    await get_resource_app_service().register_resources(module, declarations, operator_id)
