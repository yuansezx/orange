from datetime import datetime, UTC

from loguru import logger

from app.core.application.dto import RequestMeta
from app.core.domain.event_bus import EventBus
from app.core.domain.value_objects import EventId
from app.core.utils.file_type import detect_mime_type
from app.core.utils.schemas import PageResult
from app.iam.application.user_role_assignment.services import UserRoleApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.current_user.repositories import CurrentUserRepository
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import UserId
from app.iam.domain.user.enums import UserTypeEnum
from app.core.utils.generator import generate_password
from app.iam.application.common.decorators import requires_permission
from app.iam.application.common.exceptions import InvalidTokenException, PermissionDeniedException
from app.iam.application.common.ports import AuditLogWriterPort
from app.iam.application.current_user.ports import SessionManagerPort
from app.iam.application.common.services import AuditService, DeptRefService
from app.iam.application.user.exceptions import (
    AvatarValidationException,
    PasswordResetNotAllowedException,
    UserExistsException,
    UserNotExistException,
)
from app.iam.application.user.ports import AvatarStoragePort, StoredAvatar
from app.iam.application.user.dto import (
    CreateUserIn,
    GetUsersIn,
    MyProfileOut,
    RoleRefOut,
    UpdateMyProfileIn,
    UpdateUserIn,
    UserDetailOut,
    UserListItemOut,
    UserOut,
)
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.dept.services import DeptAccessService
from app.iam.domain.role.repositories import RoleRepository
from app.core.domain.units_of_work import InTransactionType
from app.iam.domain.user.entities import User
from app.iam.domain.user.events import UserChanged, UserHardDeleted
from app.iam.domain.user.exceptions import UserNotDeletedException
from app.iam.domain.user.repositories import UserRepository, SearchUser
from app.iam.domain.user.services import CheckUserUniqueService, UserAccessService
from app.iam.domain.user_role_assignment.repositories import UserRoleRepository


AVATAR_MAX_BYTES = 5 * 1024 * 1024
# image/apng 是 PNG 的动图扩展；libmagic 可能报 image/png 或 image/apng
AVATAR_ALLOWED_MIME = {
    'image/jpeg',
    'image/png',
    'image/apng',
    'image/webp',
    'image/gif',
}


class UserApplicationService:
    # 直接通过依赖链创建，不要每次手动创建
    def __init__(self, in_transaction: InTransactionType,
                 user_repo: UserRepository,
                 user_access_service: UserAccessService,
                 dept_access_service: DeptAccessService,
                 dept_repo: DeptRepository,
                 user_role_repo: UserRoleRepository,
                 role_repo: RoleRepository,
                 audit_service: AuditService,
                 audit_log_writer: AuditLogWriterPort,
                 dept_ref_service: DeptRefService,
                 session_manager: SessionManagerPort,
                 current_user_repo: CurrentUserRepository,
                 event_bus: EventBus,
                 avatar_storage: AvatarStoragePort | None = None):

        self.in_transaction = in_transaction
        self.user_repo = user_repo

        self.user_access_service = user_access_service
        self.dept_access_service = dept_access_service
        self.dept_repo = dept_repo
        self.user_role_repo = user_role_repo
        self.role_repo = role_repo
        self.audit_service = audit_service
        self.audit_log_writer = audit_log_writer
        self.dept_ref_service = dept_ref_service
        self.session_manager = session_manager
        self.current_user_repo = current_user_repo

        self.event_bus = event_bus
        self.avatar_storage = avatar_storage

    async def initialize_super_admin(self, username: str, password: str, nickname: str) -> None:
        """初始化首个超管（逃生舱）。

        仅当库中尚无 SUPER_ADMIN 时创建；首个用户无创建者，created_by 取自身 id。
        """
        if await self.user_repo.exists_by_user_type(UserTypeEnum.SUPER_ADMIN):
            return

        user_id = UserId.new()
        user = User.create_with_password(
            password,
            id=user_id,
            username=username,
            nickname=nickname,
            user_type=UserTypeEnum.SUPER_ADMIN,
            status=StatusEnum.ACTIVE,
            created_by=user_id,
            created_at=datetime.now(UTC),
            description='系统初始化',
        )
        async with self.in_transaction():
            await self.user_repo.create(user)

    @requires_permission('iam:user:read')
    async def get_users(self, data: GetUsersIn,
                        current_user: CurrentUser) -> PageResult[UserListItemOut]:
        # 数据范围直接读当前用户快照里已解析的规约，仓储只翻译
        scope = current_user.data_scope_spec
        page = await self.user_repo.search(
            SearchUser(**data.model_dump()), data.page_size, data.page, scope)
        users = page.data or []
        audits = await self.audit_service.build_many(users)
        items: list[UserListItemOut] = []
        for user, audit in zip(users, audits):
            fields = {**UserOut.model_validate(user, from_attributes=True).model_dump(),
                      **audit.model_dump()}
            items.append(UserListItemOut(**fields))
        return PageResult(page=page.page, page_size=page.page_size, total=page.total, data=items)

    @requires_permission('iam:user:read')
    async def get_user_detail(self, user_id: UserId,
                              current_user: CurrentUser) -> UserDetailOut:
        """用户详情——读不惧已删（回收站可见）：数据 + 审计 + 部门引用 + 已分配角色。"""
        user = await self.user_repo.get(user_id, include_deleted=True)
        if user is None:
            raise UserNotExistException(f'用户不存在：{user_id}')
        if not await self.user_access_service.can_access(
                user.id, current_user, include_deleted=True):
            raise PermissionDeniedException('无权访问该用户')

        audit = await self.audit_service.build(user)
        dept_refs = await self.dept_ref_service.build([user.dept_id]) if user.dept_id else []
        assignments = await self.user_role_repo.get_by_user_id(user.id)
        roles = sorted(await self.role_repo.get_by_ids([a.role_id for a in assignments]),
                       key=lambda role: role.code)

        fields = {**UserOut.model_validate(user, from_attributes=True).model_dump(),
                  **audit.model_dump()}
        return UserDetailOut(
            **fields,
            dept_ref=dept_refs[0] if dept_refs else None,
            roles=[RoleRefOut(id=r.id, code=r.code, name=r.name) for r in roles],
        )

    async def get_my_profile(self, current_user: CurrentUser) -> MyProfileOut:
        """自助资料——登录即可，强制本人；不复用管理员的数据范围/权限门禁。"""
        user = await self._load_self(current_user.user_id)
        return await self._build_my_profile(user)

    async def update_my_profile(self, data: UpdateMyProfileIn, current_user: CurrentUser,
                                request_meta: RequestMeta | None = None) -> MyProfileOut:
        """自助更新昵称/邮箱/手机号：唯一性排除本人、审计、清快照；会话不掉线。"""
        async with self.in_transaction():
            user = await self._load_self(current_user.user_id)
            unique_service = CheckUserUniqueService(self.user_repo)
            if not await unique_service.check_phone_unique(
                    data.phone, exclude_user_id=user.id):
                raise UserExistsException('该手机号已被注册')
            if not await unique_service.check_email_unique(
                    data.email, exclude_user_id=user.id):
                raise UserExistsException('该邮箱已被注册')

            before = {f: getattr(user, f) for f in ('nickname', 'email', 'phone')}
            user.update_profile(data.nickname, data.email, data.phone, current_user.user_id)
            after = {f: getattr(user, f) for f in ('nickname', 'email', 'phone')}
            changed = [f for f in before if before[f] != after[f]]

            await self.user_repo.update(user)
            await self.audit_log_writer.write(
                current_user=current_user,
                request_meta=request_meta,
                resource='user',
                action='update_profile',
                summary=f'更新个人资料：{user.username}',
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail={
                    'before': {f: str(v) if v else None for f, v in before.items()},
                    'after': {f: str(v) if v else None for f, v in after.items()},
                    'changed': changed,
                },
            )
        # 昵称在 CurrentUser 快照里：提交后清快照，会话不掉线
        await self.event_bus.publish(UserChanged(id=EventId.new(), user_id=user.id))
        return await self._build_my_profile(user)

    async def get_avatar(self, user_id: UserId, version: str) -> StoredAvatar | None:
        """读取头像（后端代理）；version 必须是当前 avatar_key 的末段，防盗链/枚举。"""
        if self.avatar_storage is None:
            return None
        user = await self.user_repo.get(user_id)
        if user is None or not user.avatar_key:
            return None
        if user.avatar_key.rsplit('/', 1)[-1] != version:
            return None
        return await self.avatar_storage.load(user.avatar_key)

    async def update_my_avatar(self, data: bytes, current_user: CurrentUser,
                               request_meta: RequestMeta | None = None) -> MyProfileOut:
        """自助上传头像：校验类型/大小 → 存对象 → 更新 key → 删旧对象（best-effort）。"""
        if self.avatar_storage is None:
            raise RuntimeError('未配置头像存储')
        if not data or len(data) > AVATAR_MAX_BYTES:
            raise AvatarValidationException(
                f'头像不能超过 {AVATAR_MAX_BYTES // 1024 // 1024} MB')
        content_type = detect_mime_type(data)
        if content_type not in AVATAR_ALLOWED_MIME:
            raise AvatarValidationException('仅支持 JPEG / PNG / APNG / WebP / GIF 图片')

        user = await self._load_self(current_user.user_id)
        old_key = user.avatar_key
        new_key = await self.avatar_storage.save(user.id, data, content_type)
        try:
            async with self.in_transaction():
                user.set_avatar_key(new_key, current_user.user_id)
                await self.user_repo.update(user)
                await self.audit_log_writer.write(
                    current_user=current_user,
                    request_meta=request_meta,
                    resource='user',
                    action='update_avatar',
                    summary=f'更新头像：{user.username}',
                    target_type='user',
                    target_id=str(user.id.value),
                    target_name=user.username,
                    detail={'old_key': old_key, 'new_key': new_key},
                )
        except Exception:
            await self._delete_avatar_quietly(new_key)
            raise

        if old_key:
            await self._delete_avatar_quietly(old_key)
        await self.event_bus.publish(UserChanged(id=EventId.new(), user_id=user.id))
        return await self._build_my_profile(user)

    async def delete_my_avatar(self, current_user: CurrentUser,
                               request_meta: RequestMeta | None = None) -> MyProfileOut:
        """自助清除头像：清 DB key + 删对象（best-effort）。"""
        user = await self._load_self(current_user.user_id)
        old_key = user.avatar_key
        if not old_key:
            return await self._build_my_profile(user)

        async with self.in_transaction():
            user.set_avatar_key(None, current_user.user_id)
            await self.user_repo.update(user)
            await self.audit_log_writer.write(
                current_user=current_user,
                request_meta=request_meta,
                resource='user',
                action='delete_avatar',
                summary=f'删除头像：{user.username}',
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail={'old_key': old_key},
            )

        await self._delete_avatar_quietly(old_key)
        await self.event_bus.publish(UserChanged(id=EventId.new(), user_id=user.id))
        return await self._build_my_profile(user)

    @requires_permission('iam:user:create')
    async def create_user_by_admin(self, data: CreateUserIn, current_user: CurrentUser,
                                   user_role_app_service: UserRoleApplicationService,
                                   request_meta: RequestMeta | None = None) -> tuple[User, str | None]:
        # 用户唯一性检验
        # 竞态问题交给数据库唯一性检验，不做redis分布式锁了
        unique_service = CheckUserUniqueService(self.user_repo)

        if not await unique_service.check_username_unique(data.username):
            raise UserExistsException('用户名已存在')
        if not await unique_service.check_phone_unique(data.phone):
            raise UserExistsException('该手机号已被注册')
        if not await unique_service.check_email_unique(data.email):
            raise UserExistsException('该邮箱已被注册')

        # 如果涉及部门，需要检验管理员是否能访问这些部门
        if data.dept_id:
            if not await self.dept_access_service.can_access(data.dept_id, current_user):
                raise PermissionDeniedException('无权访问该部门')

        temporary_password = None
        password = data.password
        if not password:
            password = generate_password()
            temporary_password = password

        async with self.in_transaction():
            # 创建用户（密码策略与 hash 由实体收口）
            user = await self.user_repo.create(User.create_with_password(
                password,
                id=UserId.new(),
                username=data.username,
                nickname=data.nickname,
                email=data.email,
                phone=data.phone,
                user_type=UserTypeEnum.ADMIN_CREATED,
                status=data.status,
                description=data.description,
                dept_id=data.dept_id,
                created_by=current_user.user_id,
                created_at=datetime.now(UTC),
            ))
            # 有角色创建用户角色关系，那边会检验权限
            if data.role_ids:
                await user_role_app_service.assign_roles_to_user(
                    user.id, data.role_ids, current_user, request_meta)
            await self.audit_log_writer.write(
                current_user=current_user,
                request_meta=request_meta,
                resource='user',
                action='create',
                summary=f'创建用户 {user.username}',
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail={
                    'username': user.username,
                    'user_type': user.user_type.value,
                    'dept_id': str(user.dept_id.value) if user.dept_id else None,
                    'role_ids': [str(r) for r in (data.role_ids or [])],
                },
            )
        return user, temporary_password

    @requires_permission('iam:user:update')
    async def update_user(self, data: UpdateUserIn, current_user: CurrentUser,
                          user_role_app_service: UserRoleApplicationService,
                          request_meta: RequestMeta | None = None) -> User:

        user = await self._load_accessible(data.id, current_user)

        # 如果涉及部门，检验权限
        if data.dept_id:
            if not await self.dept_access_service.can_access(data.dept_id, current_user):
                raise PermissionDeniedException('无权访问该部门')

        # 调用实体方法更改
        before = self._user_snapshot(user)
        user.change_profile(nickname=data.nickname, email=data.email, phone=data.phone,
                            description=data.description, dept_id=data.dept_id, operator_id=current_user.user_id)
        await self._change_status(user, data.status, current_user)
        after = self._user_snapshot(user)
        changed = [field for field in before if before[field] != after[field]]
        if data.role_ids is not None:
            changed.append('role_ids')

        async with self.in_transaction():
            # 存储实体
            await self.user_repo.update(user)
            # 设置角色：`[]` 也要处理（清空全部角色），故判 None 而非真假
            if data.role_ids is not None:
                await user_role_app_service.set_user_roles(
                    user.id, data.role_ids, current_user, request_meta)
            detail = {'before': before, 'after': after, 'changed': changed}
            if data.role_ids is not None:
                detail['role_ids'] = [str(r) for r in data.role_ids]
            await self.audit_log_writer.write(
                current_user=current_user,
                request_meta=request_meta,
                resource='user',
                action='update',
                summary=f'更新用户 {user.username}',
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail=detail,
            )
        # 事务已提交，通知订阅方失效该用户的快照（如昵称/部门/状态变更）
        await self.event_bus.publish(UserChanged(id=EventId.new(), user_id=user.id))
        return user

    @requires_permission('iam:user:update')
    async def set_user_status(self, user_id: UserId, status: StatusEnum,
                              current_user: CurrentUser, request_meta: RequestMeta | None = None) -> None:
        """统一启用/停用入口——与 `update_user` 共用加载/鉴权/状态变更逻辑。"""
        async with self.in_transaction():
            user = await self._load_accessible(user_id, current_user)
            previous_status = user.status
            await self._change_status(user, status, current_user)
            await self.user_repo.update(user)
            await self.audit_log_writer.write(
                current_user=current_user,
                request_meta=request_meta,
                resource='user',
                action='change_status',
                summary=f'{"启用" if status is StatusEnum.ACTIVE else "停用"}用户 {user.username}',
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail={'from': previous_status.value, 'to': status.value},
            )
        await self.event_bus.publish(UserChanged(id=EventId.new(), user_id=user_id))

    @requires_permission('iam:user:update')
    async def reset_user_password(self, user_id: UserId, new_password: str | None,
                                  current_user: CurrentUser,
                                  request_meta: RequestMeta | None = None) -> str | None:
        """管理员重置密码；不提供新密码时生成临时密码（明文只回传一次）。"""
        temporary_password = None
        if not new_password:
            new_password = generate_password()
            temporary_password = new_password

        async with self.in_transaction():
            user = await self._load_accessible(user_id, current_user)
            if user.id == current_user.user_id:
                raise PasswordResetNotAllowedException('不能重置自己的密码，请使用「修改密码」')
            if (user.user_type is UserTypeEnum.SUPER_ADMIN
                    and current_user.user_type is not UserTypeEnum.SUPER_ADMIN):
                raise PermissionDeniedException('无权重置超级管理员密码')
            user.reset_password(new_password, current_user.user_id)
            await self.user_repo.update(user)
            await self.audit_log_writer.write(
                current_user=current_user,
                request_meta=request_meta,
                resource='user',
                action='reset_password',
                summary=f'重置用户 {user.username} 的密码',
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail={'generated': temporary_password is not None},
            )
        # 会话在 Redis，无法回滚：事务提交后再踢，失败只影响旧令牌的存活时间
        await self.session_manager.revoke_users({user.id})
        await self.current_user_repo.evict(user.id)
        return temporary_password

    @requires_permission('iam:user:delete')
    async def delete_user(self, user_id: UserId, current_user: CurrentUser,
                          request_meta: RequestMeta | None = None) -> None:
        async with self.in_transaction():
            user = await self._load_accessible(user_id, current_user)
            previous_status = user.status
            user.delete(current_user.user_id)
            await self.user_repo.update(user)
            await self.audit_log_writer.write(
                current_user=current_user,
                request_meta=request_meta,
                resource='user',
                action='delete',
                summary=f'删除用户 {user.username}',
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail={'previous_status': previous_status.value},
            )
        await self.event_bus.publish(UserChanged(id=EventId.new(), user_id=user_id))

    @requires_permission('iam:user:delete')
    async def restore_user(self, user_id: UserId, current_user: CurrentUser,
                           request_meta: RequestMeta | None = None) -> None:
        """从回收站恢复（复用 `delete` 权限码）。"""
        async with self.in_transaction():
            user = await self._load_any(user_id)
            if not user.is_deleted:
                raise UserNotDeletedException('用户未被删除，无需恢复')
            if not await self.user_access_service.can_access(
                    user.id, current_user, include_deleted=True):
                raise PermissionDeniedException('无权访问该用户')
            user.restore(current_user.user_id)
            await self.user_repo.update(user)
            await self.audit_log_writer.write(
                current_user=current_user,
                request_meta=request_meta,
                resource='user',
                action='restore',
                summary=f'恢复用户 {user.username}',
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail={'status': user.status.value},
            )
        await self.event_bus.publish(UserChanged(id=EventId.new(), user_id=user_id))

    @requires_permission('iam:user:hard_delete')
    async def hard_delete_user(self, user_id: UserId, current_user: CurrentUser,
                               request_meta: RequestMeta | None = None) -> None:
        """彻底删除（物理）——只允许对已软删用户做；级联清悬空引用。"""
        async with self.in_transaction():
            user = await self._load_any(user_id)
            if not user.is_deleted:
                raise UserNotDeletedException('只能彻底删除已删除的用户')
            if not await self.user_access_service.can_access(
                    user.id, current_user, include_deleted=True):
                raise PermissionDeniedException('无权访问该用户')
            previous_status = user.status
            await self.user_role_repo.hard_delete_by_user(user.id)
            await self.dept_repo.clear_leader(user.id)
            await self.user_repo.hard_delete(user.id)
            await self.audit_log_writer.write(
                current_user=current_user,
                request_meta=request_meta,
                resource='user',
                action='hard_delete',
                summary=f'彻底删除用户 {user.username}',
                target_type='user',
                target_id=str(user.id.value),
                target_name=user.username,
                detail={'previous_status': previous_status.value},
            )
        # 行已不在；清快照让持有者会话按「用户不可用」失效
        await self.event_bus.publish(UserChanged(id=EventId.new(), user_id=user_id))
        # 供其他模块清理属于该用户的数据（当前总线 best-effort）
        await self.event_bus.publish(UserHardDeleted(id=EventId.new(), user_id=user_id))

    # ---------------- 内部 ----------------
    @staticmethod
    def _user_snapshot(user: User) -> dict:
        return {
            'nickname': user.nickname,
            'email': str(user.email) if user.email else None,
            'phone': str(user.phone) if user.phone else None,
            'description': user.description,
            'dept_id': str(user.dept_id.value) if user.dept_id else None,
            'status': user.status.value,
        }

    async def _load_accessible(self, user_id: UserId, current_user: CurrentUser) -> User:
        user = await self._load(user_id)
        if not await self.user_access_service.can_access(user.id, current_user):
            raise PermissionDeniedException('无权访问该用户')
        return user

    async def _change_status(self, user: User, status: StatusEnum,
                             current_user: CurrentUser) -> None:
        """状态变更的唯一应用层入口（更新 / 专用状态接口共用）。"""
        user.change_status(status, current_user.user_id)

    async def _delete_avatar_quietly(self, key: str) -> None:
        """删除对象失败不阻断主流程（只告警）。"""
        if self.avatar_storage is None:
            return
        try:
            await self.avatar_storage.delete(key)
        except Exception:
            logger.warning('删除头像对象失败：{}', key)

    async def _load_self(self, user_id: UserId) -> User:
        """自助入口固定读本人；行不存在（硬删/异常）按令牌失效处理。"""
        user = await self.user_repo.get(user_id)
        if user is None:
            raise InvalidTokenException('用户不可用')
        return user

    async def _build_my_profile(self, user: User) -> MyProfileOut:
        dept_refs = await self.dept_ref_service.build([user.dept_id]) if user.dept_id else []
        assignments = await self.user_role_repo.get_by_user_id(user.id)
        roles = sorted(await self.role_repo.get_by_ids([a.role_id for a in assignments]),
                       key=lambda role: role.code)
        return MyProfileOut(
            user_id=user.id,
            username=user.username,
            nickname=user.nickname or user.username,
            email=user.email,
            phone=user.phone,
            user_type=user.user_type,
            status=user.status,
            description=user.description,
            dept=dept_refs[0] if dept_refs else None,
            roles=[RoleRefOut(id=r.id, code=r.code, name=r.name) for r in roles],
            created_at=user.created_at,
            updated_at=user.updated_at,
            password_updated_at=user.password_updated_at,
            need_change_password=user.need_change_password,
            avatar_key=user.avatar_key,
        )

    async def _load(self, user_id: UserId) -> User:
        """写侧加载：仓储默认不返回已删（回收站操作走 `_load_any`）。"""
        user = await self.user_repo.get(user_id)
        if user is None:
            raise UserNotExistException(f'用户不存在：{user_id}')
        return user

    async def _load_any(self, user_id: UserId) -> User:
        """读侧加载：显式含已删（回收站恢复 / 彻底删除用）。"""
        user = await self.user_repo.get(user_id, include_deleted=True)
        if user is None:
            raise UserNotExistException(f'用户不存在：{user_id}')
        return user
