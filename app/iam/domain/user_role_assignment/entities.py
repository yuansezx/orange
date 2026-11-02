from datetime import datetime, UTC

from app.core.domain.entities import AuditableEntity
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import RoleId, UserId, UserRoleId


class UserRoleAssignment(AuditableEntity[UserId]):
    """用户-角色关系分配记录。

    一个 (用户, 角色) 只有一行：status（ACTIVE/DISABLED）表启停，deleted_at 表移除（正交）。
    DISABLED：用户/管理员暂时屏蔽某条授权——用户不必找管理员，即可在已有角色范围内自定义。
    """

    id: UserRoleId
    user_id: UserId
    role_id: RoleId
    status: StatusEnum

    def activate(self, operator_id: UserId) -> None:
        """（重）启用：置 ACTIVE、清删除痕迹、盖更新审计。用于复活已删行或启用被禁行者。"""
        self.status = StatusEnum.ACTIVE
        self.deleted_by = None
        self.deleted_at = None
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def delete(self, operator_id: UserId) -> None:
        """软删除：只写 deleted_at/by，不物理删除，不动 status。"""
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)
