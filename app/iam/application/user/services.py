from datetime import datetime, UTC

from app.core.domain.event_bus import EventBus
from app.core.utils.schemas import PageResult
from app.iam.application.user_role_assignment.services import UserRoleApplicationService
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import UserId
from app.iam.domain.user.enums import UserTypeEnum
from app.core.utils.password_hash import hash_password
from app.iam.application.common.decorators import requires_permission
from app.iam.application.common.exceptions import PermissionDeniedException
from app.iam.application.user.exceptions import UserExistsException
from app.iam.application.user.dto import CreateUserIn, UpdateUserIn, GetUsersIn
from app.iam.domain.dept.services import DeptAccessService
from app.core.domain.units_of_work import InTransactionType
from app.iam.domain.user.entities import User
from app.iam.domain.user.repositories import UserRepository, SearchUser
from app.iam.domain.user.services import CheckUserUniqueService, UserAccessService


class UserApplicationService:
    # 直接通过依赖链创建，不要每次手动创建
    def __init__(self, in_transaction: InTransactionType,
                 user_repo: UserRepository,
                 user_access_service: UserAccessService,
                 dept_access_service: DeptAccessService,
                 event_bus: EventBus):

        self.in_transaction = in_transaction
        self.user_repo = user_repo

        self.user_access_service = user_access_service
        self.dept_access_service = dept_access_service

        self.event_bus = event_bus

    async def initialize_super_admin(self, username: str, password: str, nickname: str) -> None:
        """初始化首个超管（逃生舱）。

        仅当库中尚无 SUPER_ADMIN 时创建；首个用户无创建者，created_by 取自身 id。
        """
        if await self.user_repo.exists_by_user_type(UserTypeEnum.SUPER_ADMIN):
            return

        user_id = UserId.new()
        user = User(id=user_id,
                    username=username,
                    nickname=nickname,
                    password_hash=hash_password(password),
                    user_type=UserTypeEnum.SUPER_ADMIN,
                    status=StatusEnum.ACTIVE,
                    need_change_password=True,
                    created_by=user_id,
                    created_at=datetime.now(UTC),
                    description='系统初始化')
        async with self.in_transaction():
            await self.user_repo.create(user)

    @requires_permission('iam:user:read')
    async def get_users(self, data:GetUsersIn,current_user: CurrentUser) -> PageResult[User]:
        return await self.user_repo.search(SearchUser(**data.model_dump()),data.page_size,data.page,current_user)

    @requires_permission('iam:user:create')
    async def create_user_by_admin(self, data: CreateUserIn, current_user: CurrentUser,
                                   user_role_app_service: UserRoleApplicationService) -> User:
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

        async with self.in_transaction():
            # 创建用户
            user = await self.user_repo.create(User(id=UserId.new(),
                                                    password_hash=hash_password(data.password),
                                                    user_type=UserTypeEnum.ADMIN_CREATED,
                                                    need_change_password=True,
                                                    created_by=current_user.user_id,
                                                    created_at=datetime.now(UTC),
                                                    **data.model_dump()))
            # 有角色创建用户角色关系，那边会检验权限
            if data.role_ids:
                await user_role_app_service.assign_roles_to_user(user.id, data.role_ids, current_user)
        return user

    @requires_permission('iam:user:update')
    async def update_user(self, data: UpdateUserIn, current_user: CurrentUser,
                          user_role_app_service: UserRoleApplicationService) -> User:

        # 当前用户是否有权限操作目标用户
        if not await self.user_access_service.can_access(data.id, current_user):
            raise PermissionDeniedException('无权访问该用户')

        user = await self.user_repo.get(data.id)

        # 如果涉及部门，检验权限
        if data.dept_id:
            if not await self.dept_access_service.can_access(data.dept_id, current_user):
                raise PermissionDeniedException('无权访问该部门')

        # 调用实体方法更改
        user.change_profile(nickname=data.nickname, email=data.email, phone=data.phone,
                            description=data.description, dept_id=data.dept_id, operator_id=current_user.user_id)
        user.change_status(data.status, current_user.user_id)

        async with self.in_transaction():
            # 存储实体
            await self.user_repo.update(user)
            # 设置角色
            if data.role_ids:
                await user_role_app_service.set_user_roles(user.id, data.role_ids, current_user)
        return user


    # async def delete_users(self,user_ids: list[int], current_user: CurrentUser) -> None:
