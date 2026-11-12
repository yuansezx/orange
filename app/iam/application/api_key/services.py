from datetime import datetime, timedelta, UTC

from loguru import logger

from app.core.application.dto import RequestMeta
from app.core.domain.units_of_work import InTransactionType
from app.core.exceptions import PersistenceException
from app.iam.application.api_key.dto import (
    ApiKeyAdminOut,
    ApiKeyCreatedOut,
    ApiKeyOut,
    CreateApiKeyIn,
    GetApiKeysIn,
    PermissionCandidateOut,
    ResourceCandidateOut,
    UpdateApiKeyIn,
)
from app.iam.application.api_key.exceptions import (
    ApiKeyDataScopeNotAllowedException,
    ApiKeyNotFoundException,
    ApiKeyScopeNotGrantedException,
    SuperAdminApiKeyNotAllowedException,
)
from app.iam.application.common.decorators import requires_permission, requires_session
from app.iam.application.common.exceptions import (
    InvalidTokenException,
    PermissionDeniedException,
)
from app.iam.application.common.ports import AuditLogWriterPort
from app.iam.application.common.services import CurrentUserSnapshotService
from app.iam.domain.api_key.entities import ApiKey
from app.iam.domain.api_key.exceptions import InvalidApiKeyTokenException
from app.iam.domain.api_key.repositories import ApiKeyRepository
from app.iam.domain.api_key.services import ApiKeyAccessService
from app.iam.domain.api_key.value_objects import ApiKeyToken
from app.iam.domain.current_user.entities import AuthContext, CurrentUser
from app.iam.domain.resource.repositories import ResourceRepository
from app.iam.domain.shared.enums import AuthMethodEnum, DataScopeEnum, StatusEnum
from app.iam.domain.shared.value_objects import ApiKeyId, DeptId, UserId
from app.iam.domain.user.enums import UserTypeEnum
from app.iam.domain.user.repositories import UserRepository

# last_used 的节流窗口：同一把 key 最多每 5 分钟写一次
LAST_USED_THROTTLE_SECONDS = 300
DEFAULT_EXPIRY_DAYS = 90

_AUDIT_VERBS = {'create': '创建', 'update': '更新', 'status': '变更状态', 'delete': '吊销'}

# API Key 不能授予「管理 API Key」类权限：这些接口全部强制会话认证（@requires_session），
# key 调用必然失败。授权与候选共用同一判定，避免出现「能选但不可用」的 scope。
# 真正的安全边界是 @requires_session；这里的过滤只是语义统一。
_API_KEY_MANAGEMENT_SCOPE_PREFIX = 'iam:api_key:'


def _is_grantable_scope(code: str) -> bool:
    return not code.startswith(_API_KEY_MANAGEMENT_SCOPE_PREFIX)


class ApiKeyAuthenticationService:
    """API Key 认证：凭据 → 用户快照 → 按 key 选择项收窄。

    超管（逃生舱）不允许持有 API Key：创建时拒绝，认证时 fail-closed
    （覆盖「创建后被提升为超管」的情况）。
    """

    def __init__(self, *, api_key_repo: ApiKeyRepository,
                 current_user_snapshot: CurrentUserSnapshotService) -> None:
        self.api_key_repo = api_key_repo
        self.current_user_snapshot = current_user_snapshot

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

        base = await self.current_user_snapshot.get_by_id(key.user_id)
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


class ApiKeyApplicationService:
    """API Key 自助管理 + 管理员管控。

    自助接口只允许操作本人 key；管理接口按 `iam:api_key:*` 功能权限 + 数据范围限制。
    所有管理操作都要求交互式会话（API Key 不能管理 key，防止泄露凭据续命）。
    """

    def __init__(self, *, api_key_repo: ApiKeyRepository,
                 user_repo: UserRepository,
                 resource_repo: ResourceRepository,
                 audit_log_writer: AuditLogWriterPort,
                 in_transaction: InTransactionType) -> None:
        self.api_key_repo = api_key_repo
        self.user_repo = user_repo
        self.resource_repo = resource_repo
        self.audit_log_writer = audit_log_writer
        self.in_transaction = in_transaction

    # ---------------- 自助 ----------------

    @requires_session
    async def list_my(self, current_user: CurrentUser) -> list[ApiKeyOut]:
        keys = await self.api_key_repo.get_all(user_id=current_user.user_id)
        return [_to_out(k) for k in keys]

    @requires_session
    async def create(self, data: CreateApiKeyIn, current_user: CurrentUser,
                     request_meta: RequestMeta | None = None) -> ApiKeyCreatedOut:
        if current_user.user_type is UserTypeEnum.SUPER_ADMIN:
            raise SuperAdminApiKeyNotAllowedException('超级管理员不允许创建 API Key')
        scopes = [code for code in data.scopes if _is_grantable_scope(code)]
        self._validate_scopes(scopes, current_user)
        self._validate_data_scope(data.data_scope_kind, data.data_scope_dept_ids, current_user)

        now = datetime.now(UTC)
        expires_at = (data.expires_at if 'expires_at' in data.model_fields_set
                      else now + timedelta(days=DEFAULT_EXPIRY_DAYS))
        token = ApiKeyToken.generate()
        key = ApiKey(
            id=ApiKeyId.new(), user_id=current_user.user_id, name=data.name,
            token_hash=token.digest, token_masked=token.masked,
            scopes=frozenset(scopes),
            data_scope_kind=data.data_scope_kind,
            data_scope_dept_ids=frozenset(data.data_scope_dept_ids),
            status=StatusEnum.ACTIVE, expires_at=expires_at,
            created_at=now, created_by=current_user.user_id,
        )
        async with self.in_transaction():
            await self.api_key_repo.create(key)
            await self._audit('create', key, current_user, request_meta, detail={
                'scopes': sorted(key.scopes),
                'data_scope_kind': key.data_scope_kind.value,
                'expires_at': _iso(key.expires_at),
            })
        return ApiKeyCreatedOut(**_to_out(key).model_dump(), token=token.value)

    @requires_session
    async def update(self, api_key_id: ApiKeyId, data: UpdateApiKeyIn,
                     current_user: CurrentUser,
                     request_meta: RequestMeta | None = None) -> ApiKeyOut:
        key = await self._load_own(api_key_id, current_user)
        scopes = [code for code in data.scopes if _is_grantable_scope(code)]
        self._validate_scopes(scopes, current_user)
        self._validate_data_scope(data.data_scope_kind, data.data_scope_dept_ids, current_user)

        key.rename(data.name, current_user.user_id)
        key.change_scopes(scopes, current_user.user_id)
        key.change_data_scope(data.data_scope_kind, data.data_scope_dept_ids,
                              current_user.user_id)
        key.change_expiry(data.expires_at, current_user.user_id)
        async with self.in_transaction():
            await self.api_key_repo.update(key)
            await self._audit('update', key, current_user, request_meta, detail={
                'scopes': sorted(key.scopes),
                'data_scope_kind': key.data_scope_kind.value,
                'expires_at': _iso(key.expires_at),
            })
        return _to_out(key)

    @requires_session
    async def change_status(self, api_key_id: ApiKeyId, status: StatusEnum,
                            current_user: CurrentUser,
                            request_meta: RequestMeta | None = None) -> ApiKeyOut:
        key = await self._load_own(api_key_id, current_user)
        key.change_status(status, current_user.user_id)
        async with self.in_transaction():
            await self.api_key_repo.update(key)
            await self._audit('status', key, current_user, request_meta,
                              detail={'status': key.status.value})
        return _to_out(key)

    @requires_session
    async def revoke(self, api_key_id: ApiKeyId, current_user: CurrentUser,
                     request_meta: RequestMeta | None = None) -> None:
        key = await self._load_own(api_key_id, current_user)
        key.delete(current_user.user_id)
        async with self.in_transaction():
            await self.api_key_repo.update(key)
            await self._audit('delete', key, current_user, request_meta)

    @requires_session
    async def scope_candidates(self, current_user: CurrentUser) -> list[ResourceCandidateOut]:
        """当前用户可授予给 key 的权限（按 module → resource → action 分组）。"""
        granted = set(current_user.permission_codes or ())
        resources = await self.resource_repo.get_all(status=StatusEnum.ACTIVE)
        result: list[ResourceCandidateOut] = []
        for resource in resources:
            permissions = [
                PermissionCandidateOut(code=p.full_code(resource), action=p.action, name=p.name)
                for p in resource.permissions
                if p.status is StatusEnum.ACTIVE
                and p.full_code(resource) in granted
                and _is_grantable_scope(p.full_code(resource))
            ]
            if permissions:
                permissions.sort(key=lambda p: p.action)
                result.append(ResourceCandidateOut(
                    module=resource.module, resource=resource.code,
                    name=resource.name, permissions=permissions))
        result.sort(key=lambda r: (r.module, r.resource))
        return result

    # ---------------- 管理员 ----------------

    @requires_session
    @requires_permission('iam:api_key:read')
    async def list_all(self, filters: GetApiKeysIn,
                       current_user: CurrentUser) -> list[ApiKeyAdminOut]:
        if (filters.user_id is not None
                and not await self._can_manage_owner(filters.user_id, current_user)):
            raise PermissionDeniedException('无权访问该用户的 API Key')

        keys = await self.api_key_repo.get_all(
            user_id=filters.user_id, status=filters.status, deleted=filters.deleted)
        if (filters.user_id is None
                and current_user.data_scope_spec.kind is not DataScopeEnum.ALL):
            allowed = await self.user_repo.get_allowed_user_ids(current_user)
            keys = [k for k in keys if k.user_id in allowed]

        owners = await self._owner_names({k.user_id for k in keys})
        result: list[ApiKeyAdminOut] = []
        for key in keys:
            username, nickname = owners.get(key.user_id, (None, None))
            result.append(ApiKeyAdminOut(
                **_to_out(key).model_dump(), user_id=key.user_id,
                username=username, nickname=nickname))
        return result

    @requires_session
    @requires_permission('iam:api_key:update')
    async def admin_change_status(self, api_key_id: ApiKeyId, status: StatusEnum,
                                  current_user: CurrentUser,
                                  request_meta: RequestMeta | None = None) -> ApiKeyAdminOut:
        key = await self._load_for_admin(api_key_id, current_user, include_deleted=False)
        key.change_status(status, current_user.user_id)
        async with self.in_transaction():
            await self.api_key_repo.update(key)
            await self._audit('status', key, current_user, request_meta,
                              detail={'status': key.status.value, 'admin': True})
        username, nickname = (await self._owner_names({key.user_id})).get(
            key.user_id, (None, None))
        return ApiKeyAdminOut(**_to_out(key).model_dump(), user_id=key.user_id,
                              username=username, nickname=nickname)

    @requires_session
    @requires_permission('iam:api_key:delete')
    async def admin_revoke(self, api_key_id: ApiKeyId, current_user: CurrentUser,
                           request_meta: RequestMeta | None = None) -> None:
        key = await self._load_for_admin(api_key_id, current_user, include_deleted=False)
        key.delete(current_user.user_id)
        async with self.in_transaction():
            await self.api_key_repo.update(key)
            await self._audit('delete', key, current_user, request_meta,
                              detail={'admin': True})

    # ---------------- 内部 ----------------

    @staticmethod
    def _validate_scopes(scopes: list[str], current_user: CurrentUser) -> None:
        granted = set(current_user.permission_codes or ())
        missing = sorted(set(scopes) - granted)
        if missing:
            raise ApiKeyScopeNotGrantedException(
                f'API Key 权限超出当前用户权限：{", ".join(missing[:5])}')

    @staticmethod
    def _validate_data_scope(kind: DataScopeEnum, dept_ids: list[DeptId],
                             current_user: CurrentUser) -> None:
        if kind is not DataScopeEnum.CUSTOM:
            return
        spec = current_user.data_scope_spec
        if spec.kind is DataScopeEnum.ALL:
            return
        if spec.kind is DataScopeEnum.SELF:
            raise ApiKeyDataScopeNotAllowedException('当前用户没有部门数据范围，不能指定部门')
        if not set(dept_ids) <= set(spec.dept_ids):
            raise ApiKeyDataScopeNotAllowedException('API Key 数据范围超出当前用户可见部门')

    async def _load_own(self, api_key_id: ApiKeyId, current_user: CurrentUser) -> ApiKey:
        key = await self.api_key_repo.get(api_key_id)
        if key is None or key.user_id != current_user.user_id:
            raise ApiKeyNotFoundException('API Key 不存在')
        return key

    async def _load_for_admin(self, api_key_id: ApiKeyId, current_user: CurrentUser,
                              *, include_deleted: bool) -> ApiKey:
        key = await self.api_key_repo.get(api_key_id, include_deleted=include_deleted)
        if key is None or key.is_deleted:
            raise ApiKeyNotFoundException('API Key 不存在')
        if not await self._can_manage_owner(key.user_id, current_user):
            raise PermissionDeniedException('无权访问该用户的 API Key')
        return key

    async def _can_manage_owner(self, user_id: UserId, current_user: CurrentUser) -> bool:
        if current_user.data_scope_spec.kind is DataScopeEnum.ALL:
            return True
        return user_id in await self.user_repo.get_allowed_user_ids(current_user)

    async def _owner_names(self, user_ids: set[UserId]
                           ) -> dict[UserId, tuple[str | None, str | None]]:
        if not user_ids:
            return {}
        users = await self.user_repo.get_by_ids(list(user_ids), include_deleted=True)
        return {u.id: (u.username, u.nickname) for u in users}

    async def _audit(self, action: str, key: ApiKey, current_user: CurrentUser,
                     request_meta: RequestMeta | None, detail: dict | None = None) -> None:
        await self.audit_log_writer.write(
            resource='api_key', action=action,
            summary=f'{_AUDIT_VERBS[action]} API Key：{key.name}',
            current_user=current_user, request_meta=request_meta,
            target_type='api_key', target_id=str(key.id.value), target_name=key.name,
            detail=detail or {},
        )


def _to_out(key: ApiKey) -> ApiKeyOut:
    return ApiKeyOut(
        id=key.id, name=key.name, token_masked=key.token_masked,
        scopes=sorted(key.scopes), data_scope_kind=key.data_scope_kind,
        data_scope_dept_ids=sorted(key.data_scope_dept_ids, key=lambda d: str(d)),
        status=key.status, expires_at=key.expires_at, last_used_at=key.last_used_at,
        created_at=key.created_at, updated_at=key.updated_at,
    )


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
