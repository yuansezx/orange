from app.iam.domain.api_key.entities import ApiKey
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.enums import DataScopeEnum
from app.iam.domain.shared.value_objects import DataScopeSpec


class ApiKeyAccessService:
    """把 API Key 的选择项与用户快照合成为本次请求的生效视图（纯计算）。"""

    @staticmethod
    def effective_permission_codes(current_user: CurrentUser, api_key: ApiKey) -> list[str]:
        """生效权限 = 用户当前权限 ∩ key scopes；用户失权时 key 自动缩权。"""
        return sorted(set(current_user.permission_codes or ()) & api_key.scopes)

    @staticmethod
    def effective_data_scope(current_user: CurrentUser, api_key: ApiKey) -> DataScopeSpec:
        """生效范围 = 用户数据范围与 key 限制取更严格者（SELF > CUSTOM > ALL）。"""
        base = current_user.data_scope_spec
        match api_key.data_scope_kind:
            case DataScopeEnum.ALL:
                return base
            case DataScopeEnum.SELF:
                return DataScopeSpec.own(base.actor_id or current_user.user_id)
            case _:  # CUSTOM（实体已限制 key 只能是 ALL/SELF/CUSTOM）
                if base.kind is DataScopeEnum.ALL:
                    return DataScopeSpec.custom(api_key.data_scope_dept_ids)
                if base.kind is DataScopeEnum.SELF:
                    return DataScopeSpec.own(base.actor_id or current_user.user_id)
                return DataScopeSpec.custom(base.dept_ids & api_key.data_scope_dept_ids)
