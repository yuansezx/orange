"""iam 的仓储实现汇总。新增实体时在这里补导出。"""
from .dept import DeptRepositoryTortoiseImpl
from .permission import PermissionRepositoryTortoiseImpl
from .resource import ResourceRepositoryTortoiseImpl
from .role import RoleRepositoryTortoiseImpl
from .user import UserRepositoryTortoiseImpl
from .user_role_assignment import UserRoleRepositoryTortoiseImpl

__all__ = [
    'DeptRepositoryTortoiseImpl',
    'PermissionRepositoryTortoiseImpl',
    'ResourceRepositoryTortoiseImpl',
    'RoleRepositoryTortoiseImpl',
    'UserRepositoryTortoiseImpl',
    'UserRoleRepositoryTortoiseImpl',
]
