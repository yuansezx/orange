from datetime import datetime, UTC

from pydantic import Field, model_validator

from app.core.domain.entities import AuditableEntity
from app.iam.domain.role.enums import DataScopeEnum
from app.iam.domain.role.exceptions import InvalidRoleCodeException
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, PermissionId, RoleId, UserId



class Role(AuditableEntity[UserId]):
    """角色聚合根。`code` 为唯一标识（不可改），`name` 仅作昵称/展示。

    权限集与部门集（数据范围）是聚合的一部分，均为**其他聚合的 id 引用**（非对象），
    随聚合整体加载/保存（见 RoleRepository）。
    """

    id: RoleId
    code: str
    name: str
    data_scope: DataScopeEnum
    status: StatusEnum
    description: str | None = None
    permission_ids: set[PermissionId] = Field(default_factory=set)
    custom_dept_ids: set[DeptId] = Field(default_factory=set)

    @model_validator(mode='after')
    def _check_code(self):
        """code 非空且不含分隔符 ':'（与权限标识的分段约定保持一致）。"""
        if not self.code or ':' in self.code:
            raise InvalidRoleCodeException(f'角色 code 非法：{self.code!r}')
        return self

    def change(self, name: str, data_scope: DataScopeEnum, description: str | None, operator_id: UserId) -> None:
        """改昵称/数据范围/描述（code 不可改）。"""
        self.name = name
        self.data_scope = data_scope
        self.description = description
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def set_permissions(self, permission_ids: set[PermissionId], operator_id: UserId) -> None:
        """整体设置权限集合。"""
        self.permission_ids = set(permission_ids)
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def set_depts(self, dept_ids: set[DeptId], operator_id: UserId) -> None:
        """整体设置数据范围部门集合（CUSTOM）。"""
        self.custom_dept_ids = set(dept_ids)
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def change_status(self, status: StatusEnum, operator_id: UserId) -> None:
        self.status = status
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)

    def delete(self, operator_id: UserId) -> None:
        """软删除：只置 status=DELETED 并记录删除人/时间，不物理删除。关系集合不动。"""
        self.change_status(StatusEnum.DELETED, operator_id)
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)
