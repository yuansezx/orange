"""认证能力的防腐适配器：iam 的 token → 用户视图 → monitor 本地 CurrentUser。"""
from app.core.exceptions import BusinessBaseException
from app.iam.interface.python import get_current_user as iam_get_current_user
from app.monitor.application.common.dto import CurrentUser
from app.monitor.application.common.enums import UserTypeEnum
from app.monitor.application.common.exceptions import MonitorUnauthenticatedException
from app.monitor.application.common.ports import AuthenticationPort


class AuthenticationAdapter(AuthenticationPort):

    async def authenticate(self, token: str) -> CurrentUser:
        try:
            resp = await iam_get_current_user(token)
        except BusinessBaseException as exc:
            if exc.code == 'IAM_INVALID_TOKEN':
                raise MonitorUnauthenticatedException('无效令牌') from exc
            raise
        return CurrentUser(
            user_id=resp.user_id.value,
            username=resp.username,
            nickname=resp.nickname,
            user_type=UserTypeEnum(resp.user_type.value),
            permission_codes=frozenset(resp.permission_codes or ()),
        )
