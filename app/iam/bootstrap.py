"""iam 模块的启动钩子。

由 core 按 `core.modules` 约定动态 import 并调用（见 app/core/__init__.py 的
_run_module_bootstraps）。放独立模块而非 `__init__.py`，是为了避免 import 副作用
（任何 `import app.iam.*` 都会执行包 `__init__`）。

本模块同时**声明本模块的资源/权限目录**（IAM_RESOURCE_DECLARATIONS）：约定每个模块
都把自己的目录声明固定放在 `bootstrap.py`，启动时幂等注册。
"""
from loguru import logger

from app.core import get_event_bus
from app.iam.application.current_user.event_handlers import CurrentUserCacheInvalidationHandler
from app.iam.application.resource.dto import RegisterPermissionIn, RegisterResourceIn
from app.iam.domain.dept.events import DeptStructureChanged
from app.iam.domain.resource.events import ResourceChanged
from app.iam.domain.role.events import RoleChanged
from app.iam.domain.user.entities import SUPER_ADMIN_USERNAME
from app.iam.domain.user.events import UserChanged
from app.iam.domain.user_role_assignment.events import UserRolesChanged
from app.iam.interface.dependences import (
    get_affected_users_query,
    get_current_user_repo,
    get_permission_users_query,
    get_resource_app_service,
    get_user_app_service,
    get_user_repo,
    get_user_role_repo,
)

# 超管账户硬编码（不读配置）：用户名取自领域常量 SUPER_ADMIN_USERNAME（'admin'，保留名）
# 初始密码首次登录强制修改
SUPER_ADMIN_INITIAL_PASSWORD = 'admin123'

# ---- 本模块资源/权限目录声明 ----
# 代码声明 + 启动幂等注册（见 register_resources）。已知限制：声明被重命名/删除后旧行残留、不对账。
IAM_MODULE = 'iam'

_CRUD = (
    ('create', '创建'),
    ('read', '查看'),
    ('update', '修改'),
    ('delete', '删除'),
)


def _crud_permissions(label: str, *, hard_delete: bool = False) -> list[RegisterPermissionIn]:
    """CRUD 四码；回收站资源再加 `hard_delete`（彻底删除，独立于软删的 `delete`）。"""
    permissions = [RegisterPermissionIn(action=action, name=f'{verb}{label}')
                   for action, verb in _CRUD]
    if hard_delete:
        permissions.append(RegisterPermissionIn(action='hard_delete', name=f'彻底删除{label}'))
    return permissions


IAM_RESOURCE_DECLARATIONS: list[RegisterResourceIn] = [
    RegisterResourceIn(
        module=IAM_MODULE, code='user', name='用户资源',
        permissions=_crud_permissions('用户', hard_delete=True),
    ),
    RegisterResourceIn(
        module=IAM_MODULE, code='role', name='角色资源',
        permissions=_crud_permissions('角色', hard_delete=True),
    ),
    RegisterResourceIn(
        module=IAM_MODULE, code='dept', name='部门资源',
        permissions=_crud_permissions('部门', hard_delete=True),
    ),
    RegisterResourceIn(
        module=IAM_MODULE, code='resource', name='资源目录',
        permissions=_crud_permissions('资源', hard_delete=True),
    ),
    RegisterResourceIn(
        module=IAM_MODULE, code='permission', name='权限目录',
        permissions=_crud_permissions('权限', hard_delete=True),
    ),
]


async def bootstrap() -> None:
    """初始化首个超管（逃生舱），再按代码声明幂等注册资源/权限目录并对账。

    先订阅快照失效、后注册：对账软删条目也要能触发当前用户快照失效。
    """
    # 订阅 CurrentUser 快照的失效：用户/角色/部门/资源权限变动时清 iam:current_user:{uid}
    bus = get_event_bus()
    invalidation = CurrentUserCacheInvalidationHandler(
        get_current_user_repo(), get_user_role_repo(),
        get_affected_users_query(), get_permission_users_query())
    bus.subscribe(UserChanged, invalidation)
    bus.subscribe(UserRolesChanged, invalidation)
    bus.subscribe(RoleChanged, invalidation)
    bus.subscribe(DeptStructureChanged, invalidation)
    bus.subscribe(ResourceChanged, invalidation)
    logger.info('已订阅 CurrentUser 快照失效（User / UserRoles / Role / DeptStructure / Resource）')

    logger.info('初始化超管账户 {!r}（若不存在）', SUPER_ADMIN_USERNAME)
    await get_user_app_service().initialize_super_admin(
        username=SUPER_ADMIN_USERNAME,
        password=SUPER_ADMIN_INITIAL_PASSWORD,
        nickname=SUPER_ADMIN_USERNAME,
    )

    # 目录实体的 created_by 是 UserId，故必须以真实超管 id 作 operator
    operator_id = await get_user_repo().get_id_by_username(SUPER_ADMIN_USERNAME)
    if operator_id is None:
        logger.warning('未找到超管 id，跳过资源/权限目录注册')
        return

    logger.info('同步 iam 资源/权限目录（声明 {} 个资源；幂等 upsert + 对账软删）',
                len(IAM_RESOURCE_DECLARATIONS))
    await get_resource_app_service().register_resources(
        IAM_MODULE, IAM_RESOURCE_DECLARATIONS, operator_id)
