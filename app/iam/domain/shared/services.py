"""领域层的共享服务——跨子域/跨聚合共用。

同一个人，看「用户列表」和「角色列表」，数据范围是同一套 roles/depts 算出来的，
所以**派生**收在这里；结果存进 CurrentUser 快照，读侧直接读 `current_user.data_scope_spec`。
"""
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.role.repositories import RoleRepository
from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum
from app.iam.domain.shared.value_objects import DataScopeSpec, DeptId
from app.iam.domain.user.entities import User
from app.iam.domain.user.enums import UserTypeEnum
from app.iam.domain.user_role_assignment.repositories import UserRoleRepository


class DataScopeService:
    """解析用户的有效数据范围（DataScopeSpec）。

    超管 → ALL。其余读 ACTIVE 的 user_role → ACTIVE 的 role，按「最宽松胜出、同模式并集」合并：
    ALL 压过一切；DEPT/DEPT_AND_CHILD/CUSTOM 的部门集合并（DEPT_AND_CHILD 用部门树 ancestors 展开）；
    仅 SELF 或无角色 → SELF。结果存进 CurrentUser 快照，读侧直接 `current_user.data_scope_spec`。
    """

    def __init__(self, user_role_repo: UserRoleRepository,
                 role_repo: RoleRepository,
                 dept_repo: DeptRepository):
        self.user_role_repo = user_role_repo
        self.role_repo = role_repo
        self.dept_repo = dept_repo

    async def resolve(self, user: User) -> DataScopeSpec:
        """按用户解析并计算数据范围（快照构建时调用）。"""
        if user.user_type is UserTypeEnum.SUPER_ADMIN:
            return DataScopeSpec.all()

        assignments = await self.user_role_repo.get_by_user_id(user.id)
        role_ids = [a.role_id for a in assignments if a.status is StatusEnum.ACTIVE]
        if not role_ids:
            return DataScopeSpec.own(user.id)
        roles = [r for r in await self.role_repo.get_by_ids(role_ids) if r.status is StatusEnum.ACTIVE]
        if not roles:
            return DataScopeSpec.own(user.id)

        descendant_ids: set[DeptId] = set()
        if user.dept_id and any(r.data_scope is DataScopeEnum.DEPT_AND_CHILD for r in roles):
            descendant_ids = {d.id for d in await self.dept_repo.get_descendants(user.dept_id)}
        return self._merge(roles, user.dept_id, descendant_ids, user.id)

    def _merge(self, roles: list, own_dept_id: DeptId | None,
               descendant_ids: set[DeptId], actor_id) -> DataScopeSpec:
        if any(r.data_scope is DataScopeEnum.ALL for r in roles):
            return DataScopeSpec.all()

        dept_ids: set[DeptId] = set()
        for r in roles:
            match r.data_scope:
                case DataScopeEnum.DEPT:
                    if own_dept_id:
                        dept_ids.add(own_dept_id)
                case DataScopeEnum.DEPT_AND_CHILD:
                    if own_dept_id:
                        dept_ids.add(own_dept_id)
                    dept_ids |= descendant_ids
                case DataScopeEnum.CUSTOM:
                    dept_ids |= set(r.custom_dept_ids)
                case _:  # SELF / ALL（ALL 已提前返回）
                    pass
        # 有部门贡献 → 以 CUSTOM 承载合并后的部门集（三种 dept 模式翻译一致）；否则 SELF
        return DataScopeSpec.custom(dept_ids) if dept_ids else DataScopeSpec.own(actor_id)
