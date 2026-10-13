from datetime import datetime, UTC

from app.core.domain.event_bus import EventBus
from app.core.domain.units_of_work import InTransactionType
from app.core.domain.value_objects import EventId
from app.iam.application.common.decorators import requires_permission
from app.iam.application.dept.dto import (
    CreateDeptIn,
    DeptOut,
    DeptTreeNode,
    GetDeptsIn,
    UpdateDeptIn,
)
from app.iam.application.dept.exceptions import (
    DeptHasChildrenException,
    DeptHasUsersException,
    DeptNameConflictException,
    DeptNotFoundException,
    DeptParentUnavailableException,
)
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.dept.entities import Dept
from app.iam.domain.dept.events import DeptStructureChanged
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.dept.services import parent_chain, shift_descendant_ancestors
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId
from app.iam.domain.user.repositories import UserRepository


def _to_out(d: Dept) -> DeptOut:
    return DeptOut(
        id=d.id, name=d.name, parent_id=d.parent_id, leader_id=d.leader_id,
        email=d.email, phone=d.phone, status=d.status, description=d.description,
        created_at=d.created_at,
    )


def _build_tree(depts: list[Dept]) -> list[DeptTreeNode]:
    """扁平列表 → 嵌套树（一条查询 + 内存分组，无 N+1）。父不在集合中的当根。"""
    nodes = {d.id: DeptTreeNode(**_to_out(d).model_dump()) for d in depts}
    roots: list[DeptTreeNode] = []
    for d in depts:
        parent = nodes.get(d.parent_id)
        (parent.children if parent else roots).append(nodes[d.id])
    return roots


class DeptApplicationService:
    """部门用例：CRUD + 树。

    功能权限由 @requires_permission 判定（超管旁路）。结构变更（增/移/删）提交后发
    DeptStructureChanged，供快照失效订阅者精确定位受影响用户。
    """

    def __init__(self, in_transaction: InTransactionType,
                 dept_repo: DeptRepository,
                 user_repo: UserRepository,
                 event_bus: EventBus) -> None:
        self.in_transaction = in_transaction
        self.dept_repo = dept_repo
        self.user_repo = user_repo
        self.event_bus = event_bus

    # ---------------- 读 ----------------
    @requires_permission('iam:dept:read')
    async def get_dept_tree(self, current_user: CurrentUser) -> list[DeptTreeNode]:
        return _build_tree(await self.dept_repo.get_all())

    @requires_permission('iam:dept:read')
    async def get_depts(self, filters: GetDeptsIn, current_user: CurrentUser) -> list[DeptOut]:
        depts = await self.dept_repo.get_all()
        if filters.name:
            depts = [d for d in depts if filters.name in d.name]
        if filters.status is not None:
            depts = [d for d in depts if d.status is filters.status]
        return [_to_out(d) for d in depts]

    @requires_permission('iam:dept:read')
    async def get_dept(self, dept_id: DeptId, current_user: CurrentUser) -> DeptOut:
        return _to_out(await self._load(dept_id))

    # ---------------- 写 ----------------
    @requires_permission('iam:dept:create')
    async def create_dept(self, data: CreateDeptIn, current_user: CurrentUser) -> Dept:
        async with self.in_transaction():
            parent = await self._load_available_parent(data.parent_id)
            await self._ensure_name_unique(parent.id if parent else None, data.name, exclude_id=None)
            dept = await self.dept_repo.create(Dept(
                id=DeptId.new(),
                name=data.name,
                parent_id=parent.id if parent else None,
                ancestors=[*parent.ancestors, parent.id] if parent else [],
                leader_id=data.leader_id,
                email=data.email,
                phone=data.phone,
                status=StatusEnum.ACTIVE,
                description=data.description,
                created_at=datetime.now(UTC),
                created_by=current_user.user_id,
            ))
        await self._notify_structure_changed(parent_chain(parent))
        return dept

    @requires_permission('iam:dept:update')
    async def update_dept(self, data: UpdateDeptIn, current_user: CurrentUser) -> Dept:
        affected: set[DeptId] = set()
        async with self.in_transaction():
            dept = await self._load(data.id)
            provided = data.model_fields_set
            operator = current_user.user_id

            new_name = data.name if 'name' in provided else dept.name
            parent_changed = 'parent_id' in provided and data.parent_id != dept.parent_id
            new_parent_id = data.parent_id if 'parent_id' in provided else dept.parent_id

            if new_name != dept.name or parent_changed:
                await self._ensure_name_unique(new_parent_id, new_name, exclude_id=dept.id)

            if parent_changed:
                old_parent = await self.dept_repo.get(dept.parent_id) if dept.parent_id else None
                parent = await self._load_available_parent(data.parent_id)
                dept.move_under(parent, operator)  # 改 parent_id + ancestors，含环路校验
                for child in await self.dept_repo.get_descendants(dept.id):
                    child.ancestors = shift_descendant_ancestors(child.ancestors, dept.id, dept.ancestors)
                    child.updated_by = operator
                    child.updated_at = datetime.now(UTC)
                    await self.dept_repo.update(child)
                # 受影响 = 旧/新父祖先链的对称差（这些部门的 DEPT_AND_CHILD 展开会变）
                affected = parent_chain(old_parent) ^ parent_chain(parent)

            if {'name', 'leader_id', 'email', 'phone', 'description'} & provided:
                dept.change_profile(
                    name=new_name,
                    leader_id=data.leader_id if 'leader_id' in provided else dept.leader_id,
                    email=data.email if 'email' in provided else dept.email,
                    phone=data.phone if 'phone' in provided else dept.phone,
                    description=data.description if 'description' in provided else dept.description,
                    operator_id=operator,
                )
            if 'status' in provided and data.status is not None:
                dept.change_status(data.status, operator)

            await self.dept_repo.update(dept)
        await self._notify_structure_changed(affected)
        return dept

    @requires_permission('iam:dept:delete')
    async def delete_dept(self, dept_id: DeptId, current_user: CurrentUser) -> None:
        async with self.in_transaction():
            dept = await self._load(dept_id)
            if await self.dept_repo.has_children(dept.id):
                raise DeptHasChildrenException('存在下级部门，不允许删除')
            if await self.user_repo.exists_by_dept(dept.id):
                raise DeptHasUsersException('部门下存在用户，不允许删除')
            parent = await self.dept_repo.get(dept.parent_id) if dept.parent_id else None
            dept.delete(current_user.user_id)
            await self.dept_repo.update(dept)
        await self._notify_structure_changed(parent_chain(parent))

    # ---------------- 内部 ----------------
    async def _notify_structure_changed(self, affected: set[DeptId]) -> None:
        if affected:
            await self.event_bus.publish(
                DeptStructureChanged(id=EventId.new(), affected_dept_ids=frozenset(affected)))

    async def _load(self, dept_id: DeptId) -> Dept:
        dept = await self.dept_repo.get(dept_id)
        if dept is None or dept.status is StatusEnum.DELETED:
            raise DeptNotFoundException(f'部门不存在：{dept_id}')
        return dept

    async def _load_available_parent(self, parent_id: DeptId | None) -> Dept | None:
        if parent_id is None:
            return None
        parent = await self.dept_repo.get(parent_id)
        if parent is None or parent.status is StatusEnum.DELETED:
            raise DeptParentUnavailableException('上级部门不存在')
        if parent.status is not StatusEnum.ACTIVE:
            raise DeptParentUnavailableException('上级部门已停用')
        return parent

    async def _ensure_name_unique(self, parent_id: DeptId | None, name: str, exclude_id: DeptId | None) -> None:
        found = await self.dept_repo.get_by_parent_and_name(parent_id, name)
        if found is not None and found.id != exclude_id:
            raise DeptNameConflictException(f'同级下已存在部门：{name}')
