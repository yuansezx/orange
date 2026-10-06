from datetime import datetime, UTC

from pydantic import model_validator

from app.core.domain.entities import AuditableEntity
from app.iam.domain.user.enums import UserTypeEnum
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import Email, Phone, DeptId, UserId
from app.iam.domain.user.exceptions import PasswordPolicyViolationException, ReservedUsernameException, UserUpdateForbiddenException
from app.core.utils.password_hash import hash_password, verify_password


# 保留用户名：仅供超管（逃生舱）使用，普通用户不得占用
SUPER_ADMIN_USERNAME = 'admin'
RESERVED_USERNAMES: frozenset[str] = frozenset({SUPER_ADMIN_USERNAME})


class User(AuditableEntity[UserId]):
    id: UserId
    username: str  # 确保唯一性 # 用户名更改单独关联权限，独立于update权限
    nickname: str | None = None  # 未配置则与 username 相同（见 _default_nickname）
    password_hash: str
    email: Email | None = None  # 确保唯一性
    phone: Phone | None = None  # 确保唯一性
    user_type: UserTypeEnum
    status: StatusEnum
    need_change_password: bool  # 这两行密码相关的记录主要是为了`首次登录要修改`，`长时间没改密码提示更改`，`管理员给用户重置密码后，用户登录修改`
    password_updated_at: datetime | None = None
    description: str | None = None
    dept_id: DeptId | None = None

    @model_validator(mode='after')
    def _default_nickname(self):
        """nickname 未配置则与 username 相同。规则只在此处落地，避免多处漂移。"""
        if not self.nickname:
            self.nickname = self.username
        return self

    @model_validator(mode='after')
    def _check_reserved_username(self):
        """保留用户名仅超管可用（普通用户不得占用 admin 之类）。"""
        if self.username in RESERVED_USERNAMES and self.user_type is not UserTypeEnum.SUPER_ADMIN:
            raise ReservedUsernameException(f'用户名 {self.username!r} 为保留用户名')
        return self

    def can_update(self) -> bool:
        return self.user_type not in {UserTypeEnum.SYSTEM}

    def can_delete(self) -> bool:
        return self.user_type not in {UserTypeEnum.SYSTEM, UserTypeEnum.SUPER_ADMIN}

    def change_password(self, new_password: str):
        """
        更改密码

        Raises:
            PasswordPolicyViolationException: 违反密码策略
        """
        if verify_password(new_password, self.password_hash):
            raise PasswordPolicyViolationException('新密码不可与旧密码相同')
        self.password_hash = hash_password(new_password)

    def change_profile(self, nickname: str, email: Email | None, phone: Phone | None, description: str | None,
                       dept_id: DeptId | None, operator_id: UserId):
        if not self.can_update():
            raise UserUpdateForbiddenException('用户不可更改')
        self.nickname = nickname
        self.email = email
        self.phone = phone
        self.description = description
        self.dept_id = dept_id
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def change_status(self, status: StatusEnum, update_by: UserId):
        if not self.can_update():
            raise UserUpdateForbiddenException('用户不可更改')
        self.status = status
        self.updated_by = update_by
        self.updated_at = datetime.now(UTC)

    def delete(self, operator_id: UserId) -> None:
        """软删除：只置 status=DELETED 并记录删除人/时间，不物理删除。

        物理删除另行处理（见 StatusEnum.DELETED 的说明）。
        """
        if not self.can_delete():
            raise UserUpdateForbiddenException('用户不可删除')
        self.status = StatusEnum.DELETED
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)
