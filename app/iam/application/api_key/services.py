from datetime import datetime, timedelta, UTC

from loguru import logger

from app.core.exceptions import PersistenceException
from app.iam.application.common.exceptions import InvalidTokenException
from app.iam.application.current_user.services import CurrentUserApplicationService
from app.iam.domain.api_key.entities import ApiKey
from app.iam.domain.api_key.exceptions import InvalidApiKeyTokenException
from app.iam.domain.api_key.repositories import ApiKeyRepository
from app.iam.domain.api_key.services import ApiKeyAccessService
from app.iam.domain.api_key.value_objects import ApiKeyToken
from app.iam.domain.current_user.entities import AuthContext, CurrentUser
from app.iam.domain.shared.enums import AuthMethodEnum
from app.iam.domain.user.enums import UserTypeEnum

# last_used 的节流窗口：同一把 key 最多每 5 分钟写一次
LAST_USED_THROTTLE_SECONDS = 300


class ApiKeyAuthenticationService:
    """API Key 认证：凭据 → 用户快照 → 按 key 选择项收窄。

    超管（逃生舱）不允许持有 API Key：创建时拒绝，认证时 fail-closed
    （覆盖「创建后被提升为超管」的情况）。
    """

    def __init__(self, *, api_key_repo: ApiKeyRepository,
                 current_user_service: CurrentUserApplicationService) -> None:
        self.api_key_repo = api_key_repo
        self.current_user_service = current_user_service

    async def authenticate(self, token: str) -> CurrentUser:
        if not ApiKeyToken.is_api_key_token(token):
            raise InvalidTokenException('无效令牌')
        try:
            api_key_token = ApiKeyToken(token)
        except InvalidApiKeyTokenException:
            raise InvalidTokenException('无效令牌')

        key = await self.api_key_repo.get_by_token_hash(api_key_token.digest)
        now = datetime.now(UTC)
        if key is None or not key.can_authenticate(now):
            raise InvalidTokenException('无效令牌')

        base = await self.current_user_service.get_current_user_by_id(key.user_id)
        if base.user_type is UserTypeEnum.SUPER_ADMIN:
            raise InvalidTokenException('无效令牌')

        await self._touch_last_used(key, now)
        return base.model_copy(update={
            'permission_codes': ApiKeyAccessService.effective_permission_codes(base, key),
            'data_scope_spec': ApiKeyAccessService.effective_data_scope(base, key),
            'auth': AuthContext(
                method=AuthMethodEnum.API_KEY,
                api_key_id=key.id,
                api_key_name=key.name,
            ),
        })

    async def _touch_last_used(self, key: ApiKey, now: datetime) -> None:
        """节流写最近使用时间；bookkeeping 失败不影响认证结果。"""
        if (key.last_used_at is not None
                and now - key.last_used_at < timedelta(seconds=LAST_USED_THROTTLE_SECONDS)):
            return
        try:
            await self.api_key_repo.update_last_used(key.id, now)
        except PersistenceException:
            logger.exception('更新 API Key 最近使用时间失败：api_key_id={}', key.id)
