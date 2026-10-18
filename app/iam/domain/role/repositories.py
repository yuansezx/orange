from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.role.entities import Role
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, RoleId


class RoleRepository(BaseRepository[RoleId, Role]):
    """角色聚合仓储。

    `get`/`get_all` 返回**装配完整的聚合**（含 permission_ids / custom_dept_ids）；
    `create`/`update`/`hard_delete` 以整个聚合为单位落库（角色行 + 两张关系表）。
    关系表由本仓储独占读写；跨聚合不级联，一致性靠读路径按 ACTIVE 过滤。
    """

    @abstractmethod
    async def get_by_code(self, code: str, *, include_deleted: bool = False) -> Role | None: ...

    @abstractmethod
    async def get_by_ids(self, role_ids: list[RoleId], *,
                         include_deleted: bool = False) -> list[Role]: ...

    @abstractmethod
    async def get_all(self, status: StatusEnum | None = None, deleted: bool = False) -> list[Role]:
        """`deleted=False` 只看未删、`True` 只看回收站；`status` 只筛业务状态。"""
        ...

    @abstractmethod
    async def get_allowed_role_ids(self, current_user: CurrentUser) -> set[RoleId]: ...

    @abstractmethod
    async def remove_custom_depts(self, dept_ids: list[DeptId]) -> int:
        """物理清理悬空引用：把所有角色数据范围中这些部门的引用移除（彻底删除部门时用）。"""
        ...
