from datetime import datetime, UTC

from pydantic import BaseModel, Field

from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import RoleId, UserId, UserRoleId
from app.iam.domain.user_role_assignment.entities import UserRoleAssignment
from app.iam.domain.user_role_assignment.repositories import UserRoleRepository


class RoleAssignmentPlan(BaseModel):
    """一次「把用户角色设为目标集」的变更计划。

    计算与落库分两步：应用层可在 `plan` 与 `apply` 之间做授权判定，
    授权失败时实体未被修改（`plan` 只读 + 构造，不改已加载行）。
    """
    user_id: UserId
    to_activate: list[UserRoleAssignment] = Field(default_factory=list)
    to_create: list[UserRoleAssignment] = Field(default_factory=list)
    to_remove: list[UserRoleAssignment] = Field(default_factory=list)

    @property
    def added(self) -> set[RoleId]:
        return {a.role_id for a in (*self.to_activate, *self.to_create)}

    @property
    def removed(self) -> set[RoleId]:
        return {a.role_id for a in self.to_remove}


class UserRoleAssignmentService:
    """用户↔角色分配规则。

    关系模型为"一行/状态翻转"：一个 (用户, 角色) 只有一行。重加曾被移除的角色时，
    复活已删行而非新插（否则撞 UNIQUE(user_id, role_id)）；移除写软删，不物理删。
    """

    def __init__(self, user_role_repo: UserRoleRepository):
        self.user_role_repo = user_role_repo

    async def plan(self, user_id: UserId, desired_role_ids: list[RoleId] | set[RoleId],
                   operator_id: UserId) -> RoleAssignmentPlan:
        """按目标集计算增删：已删行待复活、无行待新建、目标外的 ACTIVE 行待软删。"""
        desired = set(desired_role_ids)
        existing = await self.user_role_repo.get_by_user_id(user_id, include_deleted=True)
        by_role = {a.role_id: a for a in existing}
        active = {a.role_id for a in existing
                  if not a.is_deleted and a.status is StatusEnum.ACTIVE}

        plan = RoleAssignmentPlan(user_id=user_id)
        for role_id in desired - active:
            if role_id in by_role:
                plan.to_activate.append(by_role[role_id])
            else:
                plan.to_create.append(UserRoleAssignment(
                    id=UserRoleId.new(),
                    user_id=user_id,
                    role_id=role_id,
                    status=StatusEnum.ACTIVE,
                    created_at=datetime.now(UTC),
                    created_by=operator_id,
                ))
        plan.to_remove.extend(by_role[role_id] for role_id in active - desired)
        return plan

    async def apply(self, plan: RoleAssignmentPlan, operator_id: UserId) -> None:
        for assignment in plan.to_activate:
            assignment.activate(operator_id)
            await self.user_role_repo.update(assignment)
        for assignment in plan.to_remove:
            assignment.delete(operator_id)
            await self.user_role_repo.update(assignment)
        if plan.to_create:
            await self.user_role_repo.bulk_create(plan.to_create)
