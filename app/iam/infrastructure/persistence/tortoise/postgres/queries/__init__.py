"""iam 的查询实现汇总（CQRS 读侧）。新增查询时在这里补导出。"""
from .effective_permission import EffectivePermissionQueryTortoiseImpl

__all__ = ['EffectivePermissionQueryTortoiseImpl']
