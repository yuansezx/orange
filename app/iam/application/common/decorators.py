"""应用层鉴权装饰器。

只覆盖**功能权限**（是否具备 `module:resource:action`）；**数据权限**（能否操作某具体资源）
随调用而异、需查库，仍由应用服务显式调用 access service 判定。

约定：被装饰方法必须带名为 `current_user` 的 `CurrentUser` 参数（按名绑定）。
"""
import functools
import inspect

from app.iam.application.common.exceptions import PermissionDeniedException
from app.iam.domain.current_user.entities import CurrentUser


def requires_permission(*groups: str | tuple[str, ...]):
    """功能权限门禁（超管旁路由 `CurrentUser` 兜住）。

    **逗号分隔的参数之间「或」；元组内的权限码之间「与」**（DNF）。例：
      `requires_permission('a', 'b')`         ⇔ a ∨ b
      `requires_permission(('a', 'b'), 'c')`  ⇔ (a ∧ b) ∨ c

    **空参定义期报错**：空的「要求」= 不需要任何权限 = 等同于不装饰，几乎必是漏填码的 bug；
    且「看着被保护、其实全放行」是最危险的静默漏洞，故在此挡下。此与 `CurrentUser.has_permission`
    的空真**有意不对称**（谓词问「是否满足要求」，闸门表达「这是一条要求」）。

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
                raise PermissionDeniedException('权限不足')
            return await func(*args, **kwargs)

        return wrapper

    return decorator
