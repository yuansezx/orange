from loguru import logger

from app.core.application.dto import RequestMeta
from app.core.domain.units_of_work import InTransactionType
from app.core.exceptions import PersistenceException
from app.core.utils.password_hash import verify_password
from app.iam.application.common.exceptions import AuthenticationException, InvalidTokenException
from app.iam.application.common.ports import AuditLogWriterPort
from app.iam.application.common.queries import EffectivePermissionQuery
from app.iam.application.current_user.dto import LoginIn, LoginOut
from app.iam.application.current_user.ports import TokenManagerPort, TokenVerificationException
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.current_user.repositories import CurrentUserRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.services import DataScopeService
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
                 data_scope_service: DataScopeService,
                 token_manager: TokenManagerPort,
                 audit_log_writer: AuditLogWriterPort,
                 in_transaction: InTransactionType) -> None:
        self.user_repo = user_repo
        self.current_user_repo = current_user_repo
        self.effective_permission_query = effective_permission_query
        self.data_scope_service = data_scope_service
        self.token_manager = token_manager
        self.audit_log_writer = audit_log_writer
        self.in_transaction = in_transaction

    async def login(self, data: LoginIn, request_meta: RequestMeta | None = None) -> LoginOut:
        user = await self.user_repo.get_by_username(data.username)
        # 凭据错/不存在一律同一口径，不泄露存在性
        # 仓储默认不返回已删用户：已删与不存在同一口径，不泄露存在性
        if user is None or not verify_password(data.password, user.password_hash):
            await self._audit_login_failure(data.username, user, 'invalid_credentials', request_meta)
            raise AuthenticationException('用户名或密码错误')
        if user.status is not StatusEnum.ACTIVE:
            await self._audit_login_failure(data.username, user, 'disabled', request_meta)
            raise AuthenticationException('账户不可用')

        current_user = await self._build_current_user(user)
        # 成功审计失败即登录失败（fail-closed）：认证事件不留痕是安全风险
        await self._audit_login_success(current_user, request_meta)

        ttl = IAM_SETTINGS.jwt_config.expire_minutes * 60
        token = await self.token_manager.create(user.id, ttl)
        await self.current_user_repo.set(current_user)
        return LoginOut(
            access_token=token,
            expires_in=ttl,
            need_change_password=user.need_change_password,
        )

    async def get_current_user(self, token: str) -> CurrentUser:
        try:
            user_id = await self.token_manager.authenticate(token)
        except TokenVerificationException:
            raise InvalidTokenException('无效令牌')
        current_user = await self.current_user_repo.get(user_id)
        if current_user is not None:
            return current_user
        # 快照缺失（过期/被清）→ 重解析并回填，不要求重登
        user = await self.user_repo.get(user_id)  # 仓储默认不返回已删
        if user is None or user.status is not StatusEnum.ACTIVE:
            raise InvalidTokenException('用户不可用')
        current_user = await self._build_current_user(user)
        await self.current_user_repo.set(current_user)
        return current_user

    async def logout(self, token: str) -> None:
        try:
            await self.token_manager.revoke(token)
        except TokenVerificationException:
            raise InvalidTokenException('无效令牌')

    async def logout_all(self, user_id: UserId) -> None:
        await self.token_manager.revoke_all(user_id)
        await self.current_user_repo.evict(user_id)

    # ---------------- 内部 ----------------
    async def _build_current_user(self, user: User) -> CurrentUser:
        effective = await self.effective_permission_query.resolve(user.id)
        data_scope_spec = await self.data_scope_service.resolve(user)
        return CurrentUser(
            user_id=user.id,
            username=user.username,
            nickname=user.nickname,
            user_type=user.user_type,
            roles=sorted(effective.roles, key=lambda r: r.code),
            dept_id=user.dept_id,
            permission_codes=sorted(effective.permission_codes),
            data_scope_spec=data_scope_spec,
        )

    async def _audit_login_success(self, current_user: CurrentUser,
                                   request_meta: RequestMeta | None) -> None:
        async with self.in_transaction():
            await self.audit_log_writer.write(
                resource='current_user',
                action='login',
                summary=f'登录：{current_user.username}',
                current_user=current_user,
                request_meta=request_meta,
                target_type='user',
                target_id=str(current_user.user_id),
                target_name=current_user.username,
                detail={'user_type': current_user.user_type.value},
            )

    async def _audit_login_failure(self, username: str, user: User | None, reason: str,
                                   request_meta: RequestMeta | None) -> None:
        """best-effort：审计故障不改变认证结果。"""
        try:
            async with self.in_transaction():
                await self.audit_log_writer.write(
                    resource='current_user',
                    action='login',
                    summary=f'登录失败：{username}',
                    current_user=None,
                    request_meta=request_meta,
                    target_type='user',
                    target_id=str(user.id) if user else None,
                    target_name=username,
                    detail={'username': username, 'reason': reason},
                    success=False,
                    error_code='IAM_AUTHENTICATION_FAILED',
                    error_message=('用户名或密码错误' if reason == 'invalid_credentials'
                                   else '账户不可用'),
                )
        except PersistenceException:
            logger.exception('写入登录失败审计时出错：username={!r}', username)
