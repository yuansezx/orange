from datetime import datetime, UTC

from app.core.domain.entities import AuditableEntity
from app.iam.domain.user.enums import UserType
from app.iam.domain.shared.enums import Status
from app.iam.domain.shared.value_objects import Email, Phone, DeptId, UserId
from app.iam.domain.user.exceptions import PasswordPolicyViolationException, UserUpdateForbiddenException
from app.iam.domain.user.ports import PasswordHasher


class User(AuditableEntity[UserId]):
    id: UserId
    username: str  # 确保唯一性 # 用户名更改单独关联权限，独立于update权限
    nickname: str
    password_hash: str
    email: Email | None = None  # 确保唯一性
    phone: Phone | None = None  # 确保唯一性
    user_type: UserType
    status: Status
    need_change_password: bool  # 这两行密码相关的记录主要是为了`首次登录要修改`，`长时间没改密码提示更改`，`管理员给用户重置密码后，用户登录修改`
    password_updated_at: datetime | None = None
    remark: str | None = None
    dept_id: DeptId | None = None

    def can_update(self) -> bool:
        return self.user_type not in {UserType.SYSTEM}

    def can_delete(self) -> bool:
        return self.user_type not in {UserType.SYSTEM, UserType.SUPER_ADMIN}

    def change_password(self, new_password: str, password_hasher: PasswordHasher):
        """
        更改密码
        Args:
            new_password: 新密码
            password_hasher: 密码加密实现

        Returns:

        Raises:
            PasswordPolicyViolationException: 违反密码策略
        """
        if password_hasher.verify_password(new_password, self.password_hash):
            raise PasswordPolicyViolationException('新密码不可与旧密码相同')
        self.password_hash = password_hasher.hash_password(new_password)

    def change_profile(self, nickname: str, email: Email | None, phone: Phone | None, remark: str | None,
                       dept_id: DeptId | None, operator_id: UserId):
        if not self.can_update():
            raise UserUpdateForbiddenException('用户不可更改')
        self.nickname = nickname
        self.email = email
        self.phone = phone
        self.remark = remark
        self.dept_id = dept_id
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def change_status(self, status: Status, update_by: UserId):
        if not self.can_update():
            raise UserUpdateForbiddenException('用户不可更改')
        self.status = status
        self.updated_by = update_by
        self.updated_at = datetime.now(UTC)
