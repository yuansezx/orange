"""iam 对外 Python API。

其他模块只允许通过这里调用 iam；调用点应收在对方 infrastructure 适配器/组合根中，
不要在 application/domain 里直接 import 本模块。
"""
from app.iam.interface.python.resource import (
    RegisterPermissionIn,
    RegisterResourceIn,
    register_module_resources,
)

__all__ = [
    'RegisterPermissionIn',
    'RegisterResourceIn',
    'register_module_resources',
]
