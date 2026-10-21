"""monitor 模块的启动钩子。

当前只注册本模块的资源/权限目录；审计日志写入、outbox relay 等后续在此启动。
"""
from loguru import logger

from app.iam.interface.python import (
    RegisterPermissionIn,
    RegisterResourceIn,
    register_module_resources,
)

MONITOR_MODULE = 'monitor'

MONITOR_RESOURCE_DECLARATIONS: list[RegisterResourceIn] = [
    RegisterResourceIn(
        module=MONITOR_MODULE,
        code='audit_log',
        name='审计日志',
        permissions=[RegisterPermissionIn(action='read', name='查看审计日志')],
    ),
]


async def bootstrap() -> None:
    """按代码声明幂等注册 monitor 的资源/权限目录。"""
    logger.info('同步 monitor 资源/权限目录（声明 {} 个资源）',
                len(MONITOR_RESOURCE_DECLARATIONS))
    await register_module_resources(MONITOR_MODULE, MONITOR_RESOURCE_DECLARATIONS)
