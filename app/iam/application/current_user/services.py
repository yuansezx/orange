from app.core.utils.password_hash import verify_password
from app.iam.application.common.exceptions import AuthenticationException, InvalidTokenException
from app.iam.application.common.queries import EffectivePermissionQuery
from app.iam.application.current_user.dto import LoginIn, LoginOut
from app.iam.application.current_user.ports import TokenManagerPort
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.current_user.repositories import CurrentUserRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import UserId
from app.iam.domain.user.entities import User
from app.iam.domain.user.repositories import UserRepository
from app.iam.infrastructure.settings import IAM_SETTINGS


class CurrentUserApplicationService:
    """登录 / 当前用户。

    写只到 Redis（令牌白名单 + 快照），不在 DB 事务内，故不注入 in_transaction。
    """

    def __init__(self, *,
                 user_repo: UserRepository,
                 current_user_repo: CurrentUserRepository,
                 effective_permission_query: EffectivePermissionQuery,
                 token_manager: TokenManagerPort) -> None:
        self.user_repo = user_repo
        self.current_user_repo = current_user_repo
        self.effective_permission_query = effective_permission_query
        self.token_manager = token_manager

    async def login(self, data: LoginIn) -> LoginOut:
        user = await self.user_repo.get_by_username(data.username)
        # 凭据错/不存在一律同一口径，不泄露存在性
        if user is None or not verify_password(data.password, user.password_hash):
            raise AuthenticationException('用户名或密码错误')
        if user.status is not StatusEnum.ACTIVE:
            raise AuthenticationException('账户不可用')

        ttl = IAM_SETTINGS.jwt_config.expire_minutes * 60
        token = await self.token_manager.create(user.id, ttl)

        current_user = await self._build_current_user(user)
        await self.current_user_repo.set(current_user)
        return LoginOut(
            access_token=token,
            expires_in=ttl,
            need_change_password=user.need_change_password,
        )

    async def get_current_user(self, token: str) -> CurrentUser:
        user_id = await self.token_manager.authenticate(token)
        current_user = await self.current_user_repo.get(user_id)
        if current_user is not None:
            return current_user
        # 快照缺失（过期/被清）→ 重解析并回填，不要求重登
        user = await self.user_repo.get(user_id)
        if user is None or user.status is not StatusEnum.ACTIVE:
            raise InvalidTokenException('用户不可用')
        current_user = await self._build_current_user(user)
        await self.current_user_repo.set(current_user)
        return current_user

    async def logout(self, token: str) -> None:
        await self.token_manager.revoke(token)

    async def logout_all(self, user_id: UserId) -> None:
        await self.token_manager.revoke_all(user_id)
        await self.current_user_repo.evict(user_id)

    # ---------------- 内部 ----------------
    async def _build_current_user(self, user: User) -> CurrentUser:
        effective = await self.effective_permission_query.resolve(user.id)
        return CurrentUser(
            user_id=user.id,
            username=user.username,
            nickname=user.nickname,
            user_type=user.user_type,
            roles=sorted(effective.roles, key=lambda r: r.code),
            dept_id=user.dept_id,
            permission_codes=sorted(effective.permission_codes),
        )
