"""iam 的表模型汇总。

拆包后**必须**在此导出全部模型：Tortoise 只 import `...tortoise.{dialect}.models` 这一条路径，
再扫该模块的属性找模型（见 tortoise_backend._build_apps / tortoise apps.py 的 _discover_models）。
新增实体时，记得在这里补一行导出。
"""
from .dept import DeptModel
from .permission import PermissionModel
from .resource import ResourceModel
from .role import RoleModel
from .role_dept import RoleDeptModel
from .role_permission import RolePermissionModel
from .user import UserModel
from .user_role_assignment import UserRoleAssignmentModel

__all__ = [
    'DeptModel',
    'PermissionModel',
    'ResourceModel',
    'RoleModel',
    'RoleDeptModel',
    'RolePermissionModel',
    'UserModel',
    'UserRoleAssignmentModel',
]
