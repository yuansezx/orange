"""DataScopeSpec → tortoise 过滤（Q）翻译——仓储只**翻译**，不推导政策。"""
from tortoise.expressions import Q

from app.iam.domain.shared.enums import DataScopeEnum
from app.iam.domain.shared.value_objects import DataScopeSpec


def scope_filter(scope: DataScopeSpec, *, dept_field: str = 'dept_id', self_field: str = 'id') -> Q | None:
    """把 DataScopeSpec 翻成过滤条件；ALL 返回 None（不过滤）。

    dept 三态（DEPT / DEPT_AND_CHILD / CUSTOM）统一按 `scope.dept_ids` 过滤——
    具体集合由上层解析（DEPT_AND_CHILD 的部门树展开也在上层）。
    """
    match scope.kind:
        case DataScopeEnum.ALL:
            return None
        case DataScopeEnum.SELF:
            return Q(**{self_field: scope.actor_id.value})
        case DataScopeEnum.DEPT | DataScopeEnum.DEPT_AND_CHILD | DataScopeEnum.CUSTOM:
            return Q(**{f'{dept_field}__in': [d.value for d in scope.dept_ids]})
    return None
