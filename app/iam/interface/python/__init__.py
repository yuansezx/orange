"""iam 对外 Python API。

其他模块只允许通过这里调用 iam；调用点应收在对方 infrastructure 适配器/组合根中，
不要在 application/domain 里直接 import 本模块。
"""
from app.iam.interface.python.auth import CurrentUserResp, get_current_user
from app.iam.interface.python.resource import (
    RegisterPermissionReq,
    RegisterResourceReq,
    register_module_resources,
)
from app.iam.interface.python.user import (
    UserHardDeletedCallback,
    register_user_hard_deleted_listener,
)

__all__ = [
    'CurrentUserResp',
    'RegisterPermissionReq',
    'RegisterResourceReq',
    'UserHardDeletedCallback',
    'get_current_user',
    'register_module_resources',
    'register_user_hard_deleted_listener',
]
