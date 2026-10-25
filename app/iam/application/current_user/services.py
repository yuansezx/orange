from datetime import datetime, timedelta, UTC

from loguru import logger

from app.core.application.dto import RequestMeta
from app.core.domain.units_of_work import InTransactionType
from app.core.exceptions import PersistenceException
from app.core.utils.user_agent import parse_user_agent
from app.iam.application.common.decorators import requires_permission
from app.iam.application.common.exceptions import AuthenticationException, InvalidTokenException
from app.iam.application.common.ports import AuditLogWriterPort
from app.iam.application.common.queries import EffectivePermissionQuery
from app.iam.application.user.exceptions import OldPasswordMismatchException
from app.iam.application.current_user.dto import ChangePasswordIn, LoginIn, LoginOut, SessionOut
from app.iam.application.current_user.ports import (
    SessionInfo,
    SessionManagerPort,
    SessionMeta,
    SessionVerificationException,
)
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.current_user.repositories import CurrentUserRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.services import DataScopeService
from app.iam.domain.shared.value_objects import UserId
from app.iam.domain.user.entities import User
from app.iam.domain.user.repositories import UserRepository
from app.iam.infrastructure.settings import IAM_SETTINGS


class CurrentUserApplicationService:
    """登录 / 当前用户 / 在线会话。

    会话数据在 Redis（会话白名单 + 当前用户快照）；登录/踢下线审计需要 DB 事务。
    """

    def __init__(self, *,
                 user_repo: UserRepository,
                 current_user_repo: CurrentUserRepository,
                 effective_permission_query: EffectivePermissionQuery,
                 data_scope_service: DataScopeService,
                 session_manager: SessionManagerPort,
                 audit_log_writer: AuditLogWriterPort,
                 in_transaction: InTransactionType) -> None:
        self.user_repo = user_repo
        self.current_user_repo = current_user_repo
        self.effective_permission_query = effective_permission_query
        self.data_scope_service = data_scope_service
        self.session_manager = session_manager
        self.audit_log_writer = audit_log_writer
        self.in_transaction = in_transaction

    async def login(self, data: LoginIn, request_meta: RequestMeta | None = None) -> LoginOut:
        user = await self.user_repo.get_by_username(data.username)
        # 凭据错/不存在一律同一口径，不泄露存在性
        # 仓储默认不返回已删用户：已删与不存在同一口径，不泄露存在性
        if user is None or not user.verify_password(data.password):
            await self._audit_login_failure(data.username, user, 'invalid_credentials', request_meta)
            raise AuthenticationException('用户名或密码错误')
        if user.status is not StatusEnum.ACTIVE:
            await self._audit_login_failure(data.username, user, 'disabled', request_meta)
            raise AuthenticationException('账户不可用')

        current_user = await self._build_current_user(user)
        # 成功审计失败即登录失败（fail-closed）：认证事件不留痕是安全风险
        await self._audit_login_success(current_user, request_meta)

        ttl = IAM_SETTINGS.jwt_config.expire_minutes * 60
        now = datetime.now(UTC)
        meta = SessionMeta(
            login_at=now,
            expires_at=now + timedelta(seconds=ttl),
            login_ip=request_meta.ip if request_meta else None,
            login_user_agent=request_meta.user_agent if request_meta else None,
        )
        token = await self.session_manager.create(user.id, ttl, meta=meta)
        await self.current_user_repo.set(current_user)
        return LoginOut(
            access_token=token,
            expires_in=ttl,
            need_change_password=user.need_change_password,
        )

    async def get_current_user(self, token: str) -> CurrentUser:
        try:
            session = await self.session_manager.authenticate(token)
        except SessionVerificationException:
            raise InvalidTokenException('无效令牌')
        user_id = session.user_id
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
            session = await self.session_manager.authenticate(token)
        except SessionVerificationException:
            raise InvalidTokenException('无效令牌')
        await self.session_manager.revoke(session.user_id, {session.session_id})

    async def logout_all(self, user_id: UserId) -> None:
        await self.session_manager.revoke_users({user_id})
        await self.current_user_repo.evict(user_id)

    async def change_password(self, data: ChangePasswordIn, current_user: CurrentUser,
                              request_meta: RequestMeta | None = None) -> None:
        """自助改密：成功后吊销全部会话（含当前），要求重新登录。"""
        user = await self.user_repo.get(current_user.user_id)
        if user is None:
            raise InvalidTokenException('用户不可用')
        if not user.verify_password(data.old_password):
            raise OldPasswordMismatchException('旧密码不正确')
        user.change_password(data.new_password, current_user.user_id)

        async with self.in_transaction():
            await self.user_repo.update(user)
            await self.audit_log_writer.write(
                resource='user',
                action='change_password',
                summary=f'修改密码：{user.username}',
                current_user=current_user,
                request_meta=request_meta,
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail={'self': True},
            )
        # 会话在 Redis，无法回滚：事务提交后再踢，失败只影响旧令牌的存活时间
        await self.session_manager.revoke_users({user.id})
        await self.current_user_repo.evict(user.id)

    # ---------------- 在线会话 ----------------
    @requires_permission('iam:current_user:read_sessions')
    async def list_sessions(self, current_user: CurrentUser) -> list[SessionOut]:
        sessions = await self.session_manager.get_all()
        names = await self._resolve_user_names({s.user_id for s in sessions})
        result = [_to_session_out(s, names.get(s.user_id, (None, None))) for s in sessions]
        result.sort(key=lambda s: s.login_at, reverse=True)
        return result

    @requires_permission('iam:current_user:revoke_sessions')
    async def revoke_sessions(self, user_id: UserId, session_ids: list[str] | set[str],
                              current_user: CurrentUser,
                              request_meta: RequestMeta | None = None) -> int:
        ids = set(session_ids)
        if not ids:
            return 0
        removed = await self.session_manager.revoke(user_id, ids)
        if removed:
            await self._audit_revoke(
                target_id=str(user_id),
                summary=f'踢下线：{user_id}',
                action='revoke_sessions',
                detail={'session_ids': sorted(ids)},
                current_user=current_user, request_meta=request_meta)
        return removed

    @requires_permission('iam:current_user:revoke_users')
    async def revoke_users(self, user_ids: list[UserId] | set[UserId],
                           current_user: CurrentUser,
                           request_meta: RequestMeta | None = None) -> int:
        ids = set(user_ids)
        if not ids:
            return 0
        deleted = await self.session_manager.revoke_users(ids)
        if deleted:
            await self._audit_revoke(
                target_id=None,
                summary=f'批量踢下线：{len(ids)} 个用户',
                action='revoke_users',
                detail={'user_ids': sorted(str(u) for u in ids)},
                current_user=current_user, request_meta=request_meta)
        return deleted

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

    async def _resolve_user_names(
            self, user_ids: set[UserId]) -> dict[UserId, tuple[str | None, str | None]]:
        """快照优先、用户表回退；按 user_id 去重，避免 N+1。"""
        names: dict[UserId, tuple[str | None, str | None]] = {}
        missing: list[UserId] = []
        for user_id in user_ids:
            snapshot = await self.current_user_repo.get(user_id)
            if snapshot is not None:
                names[user_id] = (snapshot.username, snapshot.nickname)
            else:
                missing.append(user_id)
        if missing:
            for user in await self.user_repo.get_by_ids(missing, include_deleted=True):
                names[user.id] = (user.username, user.nickname)
        return names

    async def _audit_revoke(self, *, target_id: str | None, summary: str,
                            action: str, detail: dict | None,
                            current_user: CurrentUser,
                            request_meta: RequestMeta | None) -> None:
        # 会话变更在 Redis，无法回滚；审计失败只记日志，不改变操作结果
        try:
            async with self.in_transaction():
                await self.audit_log_writer.write(
                    resource='current_user',
                    action=action,
                    summary=summary,
                    current_user=current_user,
                    request_meta=request_meta,
                    target_type='user',
                    target_id=target_id,
                    detail=detail or {},
                )
        except PersistenceException:
            logger.exception('写入踢下线审计失败：action={} target={}', action, target_id)


def _to_session_out(info: SessionInfo,
                    name: tuple[str | None, str | None]) -> SessionOut:
    ua = parse_user_agent(info.login_user_agent)
    return SessionOut(
        user_id=info.user_id,
        username=name[0],
        nickname=name[1],
        session_id=info.session_id,
        login_at=info.login_at,
        expires_at=info.expires_at,
        login_ip=info.login_ip,
        login_user_agent=info.login_user_agent,
        browser=ua.browser,
        browser_version=ua.browser_version,
        os=ua.os,
        device=ua.device,
    )
