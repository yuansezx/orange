"""monitor 的 tortoise 模型汇总。

模型必须在本模块导出，否则 Tortoise 按约定发现不到。
"""
from .audit_log import AuditLogModel

__all__ = ['AuditLogModel']
