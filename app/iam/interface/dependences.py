"""iam 模块的依赖装配（组合根）。

- HTTP 路由经 FastAPI `Depends` 调用这里的 `get_*`；
- bootstrap / python api 等非 HTTP 入口手动调用同一批 `get_*`。

注意：这里没有容器，每次 `get_*` 都会 new 出新实例（HTTP 侧由 Depends 的
per-request 缓存兜住）。所以被装配的实现应是**无状态**的。

方言实现经 `persistence.module_infra(模块, 子模块)` 取：方言由模块的连接决定，
组合根**不硬编码方言**（返回的是模块，属性即实现类）。
"""
from redis.asyncio import Redis

from app.core import get_event_bus
from app.core.domain.units_of_work import InTransactionType
from app.core.infrastructure import cache, persistence
from app.iam.application.common.queries import EffectivePermissionQuery
from app.iam.application.current_user.ports import TokenManagerPort
from app.iam.application.current_user.services import CurrentUserApplicationService
from app.iam.application.resource.services import ResourceApplicationService
from app.iam.application.role.services import RoleApplicationService
from app.iam.application.user.services import UserApplicationService
from app.iam.application.user_role_assignment.services import UserRoleApplicationService
from app.iam.domain.current_user.repositories import CurrentUserRepository
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.dept.services import DeptAccessService
from app.iam.domain.permission.repositories import PermissionRepository
from app.iam.domain.resource.repositories import ResourceRepository
from app.iam.domain.role.repositories import RoleRepository
from app.iam.domain.role.services import RoleAccessService
from app.iam.domain.user.repositories import UserRepository
from app.iam.domain.user.services import UserAccessService
from app.iam.domain.user_role_assignment.repositories import UserRoleRepository
from app.iam.infrastructure.adapters.token_manager_adapter import TokenManagerJWTRedisAdapter
from app.iam.infrastructure.cache.current_user_repo import CurrentUserRepositoryRedisImpl

# 按当前连接的方言解析 iam 的基础设施实现（models / repositories / queries）
_repos = persistence.module_infra('iam', 'repositories')
_queries = persistence.module_infra('iam', 'queries')


def get_in_transaction() -> InTransactionType:
    return persistence.get_in_transaction()


def get_user_repo() -> UserRepository:
    return _repos.UserRepositoryTortoiseImpl()


def get_dept_repo() -> DeptRepository:
    return _repos.DeptRepositoryTortoiseImpl()


def get_resource_repo() -> ResourceRepository:
    return _repos.ResourceRepositoryTortoiseImpl()


def get_permission_repo() -> PermissionRepository:
    return _repos.PermissionRepositoryTortoiseImpl()


def get_user_access_service() -> UserAccessService:
    return UserAccessService(get_user_repo())


def get_dept_access_service() -> DeptAccessService:
    return DeptAccessService(get_dept_repo())


def get_user_app_service() -> UserApplicationService:
    return UserApplicationService(
        in_transaction=get_in_transaction(),
        user_repo=get_user_repo(),
        user_access_service=get_user_access_service(),
        dept_access_service=get_dept_access_service(),
        event_bus=get_event_bus(),
    )


def get_resource_app_service() -> ResourceApplicationService:
    return ResourceApplicationService(
        in_transaction=get_in_transaction(),
        resource_repo=get_resource_repo(),
        permission_repo=get_permission_repo(),
    )


def get_role_repo() -> RoleRepository:
    return _repos.RoleRepositoryTortoiseImpl()


def get_role_access_service() -> RoleAccessService:
    return RoleAccessService(get_role_repo())


def get_role_app_service() -> RoleApplicationService:
    return RoleApplicationService(
        in_transaction=get_in_transaction(),
        role_repo=get_role_repo(),
        permission_repo=get_permission_repo(),
        role_access_service=get_role_access_service(),
    )


def get_user_role_repo() -> UserRoleRepository:
    return _repos.UserRoleRepositoryTortoiseImpl()


def get_user_role_app_service() -> UserRoleApplicationService:
    return UserRoleApplicationService(
        in_transaction=get_in_transaction(),
        user_role_repo=get_user_role_repo(),
        role_access_service=get_role_access_service(),
    )


def get_cache_client() -> Redis:
    return cache.get_cache()


def get_current_user_repo() -> CurrentUserRepository:
    return CurrentUserRepositoryRedisImpl(get_cache_client())


def get_effective_permission_query() -> EffectivePermissionQuery:
    return _queries.EffectivePermissionQueryTortoiseImpl()


def get_token_manager() -> TokenManagerPort:
    return TokenManagerJWTRedisAdapter(get_cache_client())


def get_current_user_app_service() -> CurrentUserApplicationService:
    return CurrentUserApplicationService(
        user_repo=get_user_repo(),
        current_user_repo=get_current_user_repo(),
        effective_permission_query=get_effective_permission_query(),
        token_manager=get_token_manager(),
    )
