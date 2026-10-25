from datetime import datetime, UTC

from pydantic import model_validator

from app.core.domain.entities import AuditableEntity
from app.iam.domain.user.enums import UserTypeEnum
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import Email, Phone, DeptId, UserId
from app.iam.domain.user.exceptions import (
    PasswordPolicyViolationException,
    ReservedUsernameException,
    SuperAdminSelfDisableException,
    UserImmutableException,
)
from app.core.utils.password_hash import hash_password, verify_password


# 保留用户名：仅供超管（逃生舱）使用，普通用户不得占用
SUPER_ADMIN_USERNAME = 'admin'
RESERVED_USERNAMES: frozenset[str] = frozenset({SUPER_ADMIN_USERNAME})

PASSWORD_MIN_LENGTH = 8
# bcrypt 只使用前 72 字节，超出部分会被静默截断，因此必须显式拒绝
PASSWORD_MAX_BYTES = 72


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

    @classmethod
    def create_with_password(cls, password: str, **fields) -> 'User':
        """创建用户：密码策略与哈希由实体收口（创建后首次登录需修改）。"""
        cls._validate_password(password)
        now = datetime.now(UTC)
        return cls(
            password_hash=hash_password(password),
            password_updated_at=now,
            need_change_password=True,
            **fields,
        )

    def verify_password(self, password: str) -> bool:
        """校验明文密码是否匹配（登录 / 改密旧密码校验共用）。"""
        return verify_password(password, self.password_hash)

    def change_password(self, new_password: str, operator_id: UserId) -> None:
        """自助改密：成功后不再要求修改密码。"""
        self._apply_password(new_password, operator_id, need_change_password=False)

    def reset_password(self, new_password: str, operator_id: UserId) -> None:
        """管理员重置：用户下次登录仍需修改密码。"""
        self._apply_password(new_password, operator_id, need_change_password=True)

    def _apply_password(self, new_password: str, operator_id: UserId,
                        *, need_change_password: bool) -> None:
        if not self.can_update():
            raise UserImmutableException('用户不可更改')
        self._validate_password(new_password)
        if self.verify_password(new_password):
            raise PasswordPolicyViolationException('新密码不可与旧密码相同')
        now = datetime.now(UTC)
        self.password_hash = hash_password(new_password)
        self.password_updated_at = now
        self.need_change_password = need_change_password
        self.updated_by = operator_id
        self.updated_at = now

    @staticmethod
    def _validate_password(password: str) -> None:
        if len(password) < PASSWORD_MIN_LENGTH:
            raise PasswordPolicyViolationException(f'密码长度不能少于 {PASSWORD_MIN_LENGTH} 位')
        if len(password.encode('utf-8')) > PASSWORD_MAX_BYTES:
            raise PasswordPolicyViolationException(f'密码不能超过 {PASSWORD_MAX_BYTES} 字节')

    def change_profile(self, nickname: str, email: Email | None, phone: Phone | None, description: str | None,
                       dept_id: DeptId | None, operator_id: UserId):
        if not self.can_update():
            raise UserImmutableException('用户不可更改')
        self.nickname = nickname
        self.email = email
        self.phone = phone
        self.description = description
        self.dept_id = dept_id
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def change_status(self, status: StatusEnum, update_by: UserId):
        if not self.can_update():
            raise UserImmutableException('用户不可更改')
        # 超管自停是唯一不可恢复的路径（没有其他账号能再启用它）→ 必须由别人操作
        if (status is StatusEnum.DISABLED
                and self.user_type is UserTypeEnum.SUPER_ADMIN
                and self.id == update_by):
            raise SuperAdminSelfDisableException('超级管理员不能停用自己，请先创建日常管理员')
        self.status = status
        self.updated_by = update_by
        self.updated_at = datetime.now(UTC)

    def delete(self, operator_id: UserId) -> None:
        """软删除：只写 deleted_at/by，不物理删除，**不动 status**（停用状态得以保留）。"""
        if not self.can_delete():
            raise UserImmutableException('用户不可删除')
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def restore(self, operator_id: UserId) -> None:
        """清删除痕迹（恢复）——现有 status 原样保留。是否「必须已删」由用例层判定。"""
        self.deleted_at = None
        self.deleted_by = None
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)
