"""iam 模块的依赖装配（组合根）。

- HTTP 路由经 FastAPI `Depends` 调用这里的 `get_*`；
- bootstrap / python api 等非 HTTP 入口手动调用同一批 `get_*`。

注意：这里没有容器，每次 `get_*` 都会 new 出新实例（HTTP 侧由 Depends 的
per-request 缓存兜住）。所以被装配的实现应是**无状态**的。
"""
from app.core import get_event_bus
from app.core.domain.units_of_work import InTransactionType
from app.core.infrastructure import persistence
from app.iam.application.user.services import UserApplicationService
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.dept.services import DeptAccessService
from app.iam.domain.user.repositories import UserRepository
from app.iam.domain.user.services import UserAccessService
from app.iam.infrastructure.persistence.tortoise.repositories import DeptRepositoryTortoiseImpl, UserRepositoryTortoiseImpl


def get_in_transaction() -> InTransactionType:
    return persistence.get_in_transaction()


def get_user_repo() -> UserRepository:
    return UserRepositoryTortoiseImpl()


def get_dept_repo() -> DeptRepository:
    return DeptRepositoryTortoiseImpl()


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
