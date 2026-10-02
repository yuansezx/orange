from datetime import datetime, UTC

from app.core.domain.entities import AuditableEntity
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import UserRoleId, UserId, RoleId


class UserRoleAssignment(AuditableEntity):
    """用户-角色关系分配记录"""
    id: UserRoleId
    user_id: UserId
    role_id: RoleId
    status: StatusEnum # disabled用来给用户/管理员暂时屏蔽某些角色的授权，这样用户不用找管理员即可在已有角色范围内，自定义自己的角色

    def delete(self,operator_id: UserId) -> None:
        self.status = StatusEnum.DELETED
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)