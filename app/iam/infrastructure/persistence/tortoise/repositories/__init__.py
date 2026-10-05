"""iam 的仓储实现汇总。新增实体时在这里补导出。"""
from .dept import DeptRepositoryTortoiseImpl
from .user import UserRepositoryTortoiseImpl

__all__ = ['DeptRepositoryTortoiseImpl', 'UserRepositoryTortoiseImpl']
