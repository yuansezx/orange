"""应用层鉴权装饰器（功能权限）。

约定：被装饰方法必须带名为 `current_user` 的 `CurrentUser` 参数（按名绑定）。
数据权限需查库、随对象变化，不在装饰器覆盖范围内。
"""
import functools
import inspect

from app.monitor.application.common.dto import CurrentUser
from app.monitor.application.common.exceptions import MonitorPermissionDeniedException


def requires_permission(*groups: str | tuple[str, ...]):
    """功能权限门禁。

    **参数之间「或」；元组内「与」**（DNF）；超管旁路由 `CurrentUser.has_permission` 兜住。
    **空参定义期报错**：空的「要求」= 不需要权限，等同于不装饰，几乎必是漏填码。
    被装饰方法须带名为 `current_user` 的参数（缺参数定义期报错）。
    """
    if not groups:
        raise TypeError('requires_permission：至少要给一个权限码')

    def decorator(func):
        sig = inspect.signature(func)
        if 'current_user' not in sig.parameters:
            raise TypeError(
                f'{func.__qualname__} 用 @requires_permission 装饰，但缺少 current_user 参数')

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = sig.bind(*args, **kwargs).arguments.get('current_user')
            if not isinstance(current_user, CurrentUser) or not current_user.has_permission(*groups):
                raise MonitorPermissionDeniedException('权限不足')
            return await func(*args, **kwargs)

        return wrapper

    return decorator
