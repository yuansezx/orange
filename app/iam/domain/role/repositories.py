from abc import abstractmethod

from app.core.domain.repositories import BaseRepository
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.role.entities import Role
from app.iam.domain.shared.value_objects import RoleId


class RoleRepository(BaseRepository[RoleId, Role]):
    """角色聚合仓储。

    `get`/`get_all` 返回**装配完整的聚合**（含 permission_ids / custom_dept_ids）；
    `create`/`update`/`hard_delete` 以整个聚合为单位落库（角色行 + 两张关系表）。
    关系表由本仓储独占读写；跨聚合不级联，一致性靠读路径按 ACTIVE 过滤。
    """

    @abstractmethod
    async def get_by_code(self, code: str) -> Role | None: ...

    @abstractmethod
    async def get_all(self, include_deleted: bool = False) -> list[Role]: ...

    @abstractmethod
    async def get_allowed_role_ids(self, current_user: CurrentUser) -> set[RoleId]: ...
