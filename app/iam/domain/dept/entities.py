from datetime import datetime, UTC

from pydantic import Field

from app.core.domain.entities import AuditableEntity
from app.iam.domain.dept.exceptions import DeptCycleException
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import Email, Phone, DeptId, UserId


class Dept(AuditableEntity):
    id: DeptId
    name: str
    parent_id: DeptId | None = None
    # 物化路径：从根到父的祖先 id（不含自己；根=空）。供「找子孙」走 GIN 索引单查，
    # 由 move_under 维护、move 时由应用层连带重写子孙（见 shift_descendant_ancestors）。
    ancestors: list[DeptId] = Field(default_factory=list)
    leader_id: UserId | None = None
    email: Email | None = None
    phone: Phone | None = None
    status: StatusEnum
    description: str | None = None

    def change_profile(self, name: str, leader_id: UserId | None, email: Email | None,
                       phone: Phone | None, description: str | None, operator_id: UserId) -> None:
        """改昵称/负责人/联系方式/描述（不动结构，也不动状态）。"""
        self.name = name
        self.leader_id = leader_id
        self.email = email
        self.phone = phone
        self.description = description
        self._stamp(operator_id)

    def move_under(self, parent: 'Dept | None', operator_id: UserId) -> None:
        """挂到 parent 下（None=顶级）。同步重算自身 parent_id / ancestors。

        Raises:
            DeptCycleException: 新上级是自己或自己的下级
        """
        if parent is not None and (parent.id == self.id or self.id in parent.ancestors):
            raise DeptCycleException('上级部门不能是自己或自己的下级')
        self.parent_id = parent.id if parent else None
        self.ancestors = [*parent.ancestors, parent.id] if parent else []
        self._stamp(operator_id)

    def change_status(self, status: StatusEnum, operator_id: UserId) -> None:
        self.status = status
        self._stamp(operator_id)

    def delete(self, operator_id: UserId) -> None:
        """软删除：置 status=DELETED 并记录删除人/时间，不物理删除。"""
        self.status = StatusEnum.DELETED
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)
        self._stamp(operator_id)

    def _stamp(self, operator_id: UserId) -> None:
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)
