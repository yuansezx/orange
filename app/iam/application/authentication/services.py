from app.iam.application.api_key.services import ApiKeyAuthenticationService
from app.iam.application.current_user.services import CurrentUserApplicationService
from app.iam.domain.api_key.value_objects import ApiKeyToken
from app.iam.domain.current_user.entities import CurrentUser


class AuthenticationApplicationService:
    """统一认证入口：按凭据前缀确定性路由，失败即 401，不逐个试错。"""

    def __init__(self, *, session_auth: CurrentUserApplicationService,
                 api_key_auth: ApiKeyAuthenticationService) -> None:
        self.session_auth = session_auth
        self.api_key_auth = api_key_auth

    async def authenticate(self, token: str) -> CurrentUser:
        if ApiKeyToken.is_api_key_token(token):
            return await self.api_key_auth.authenticate(token)
        return await self.session_auth.get_current_user(token)
