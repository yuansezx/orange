"""应用层鉴权装饰器。

只覆盖**功能权限**（是否具备 `module:resource:action`）；**数据权限**（能否操作某具体资源）
随调用而异、需查库，仍由应用服务显式调用 access service 判定。

约定：被装饰方法必须带名为 `current_user` 的 `CurrentUser` 参数（按名绑定）。
"""
import functools
import inspect

from app.iam.application.common.exceptions import PermissionDeniedException
from app.iam.domain.current_user.entities import CurrentUser


def requires_permission(*codes: str):
    """要求当前用户具备**全部**给定权限码，否则抛 `PermissionDeniedException`（→ 403）。

    超管旁路由 `CurrentUser.has_permission` 兜住。
    """
    def decorator(func):
        sig = inspect.signature(func)
        if 'current_user' not in sig.parameters:
            raise TypeError(
                f'{func.__qualname__} 用 @requires_permission 装饰，但缺少 current_user 参数')

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = sig.bind(*args, **kwargs).arguments.get('current_user')
            if not isinstance(current_user, CurrentUser) or not current_user.has_permission(*codes):
                raise PermissionDeniedException('权限不足')
            return await func(*args, **kwargs)

        return wrapper

    return decorator
