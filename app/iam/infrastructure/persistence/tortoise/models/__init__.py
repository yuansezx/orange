"""iam 的表模型汇总。

拆包后**必须**在此导出全部模型：Tortoise 只 import `...tortoise.models` 这一条路径，
再扫该模块的属性找模型（见 tortoise_backend._build_apps / tortoise apps.py 的 _discover_models）。
新增实体时，记得在这里补一行导出。
"""
from .dept import DeptModel
from .user import UserModel

__all__ = ['DeptModel', 'UserModel']
