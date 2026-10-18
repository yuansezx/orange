from datetime import datetime, UTC

from app.core.domain.event_bus import EventBus
from app.core.domain.units_of_work import InTransactionType
from app.core.domain.value_objects import EventId
from app.iam.application.common.decorators import requires_permission
from app.iam.application.common.exceptions import PermissionDeniedException
from app.iam.application.common.services import AuditService, DeptRefService
from app.iam.application.dept.dto import (
    CreateDeptIn,
    DeptDetailOut,
    DeptOut,
    DeptTreeNode,
    GetDeptsIn,
    UpdateDeptIn,
)
from app.iam.application.dept.exceptions import (
    DeptHasUsersException,
    DeptNameConflictException,
    DeptNotFoundException,
    DeptParentUnavailableException,
)
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.dept.entities import Dept
from app.iam.domain.dept.events import DeptStructureChanged
from app.iam.domain.dept.exceptions import DeptNotDeletedException
from app.iam.domain.dept.repositories import DeptRepository
from app.iam.domain.dept.services import DeptAccessService, parent_chain, shift_descendant_ancestors
from app.iam.domain.role.repositories import RoleRepository
from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum
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

    功能权限由 @requires_permission 判定（超管旁路）；数据范围读侧按快照 `data_scope_spec`
    过滤、写侧由 `DeptAccessService.can_access` 判定。结构变更（增/移/删）提交后发
    DeptStructureChanged，供快照失效订阅者精确定位受影响用户。
    """

    def __init__(self, in_transaction: InTransactionType,
                 dept_repo: DeptRepository,
                 user_repo: UserRepository,
                 dept_access_service: DeptAccessService,
                 audit_service: AuditService,
                 dept_ref_service: DeptRefService,
                 role_repo: RoleRepository,
                 event_bus: EventBus) -> None:
        self.in_transaction = in_transaction
        self.dept_repo = dept_repo
        self.user_repo = user_repo
        self.dept_access_service = dept_access_service
        self.role_repo = role_repo
        self.audit_service = audit_service
        self.dept_ref_service = dept_ref_service
        self.event_bus = event_bus

    # ---------------- 读 ----------------
    @requires_permission('iam:dept:read')
    async def get_dept_tree(self, current_user: CurrentUser) -> list[DeptTreeNode]:
        return _build_tree(await self._visible_depts(current_user))

    @requires_permission('iam:dept:read')
    async def get_depts(self, filters: GetDeptsIn, current_user: CurrentUser) -> list[DeptOut]:
        depts = await self._visible_depts(current_user, filters.status, filters.deleted)
        if filters.name:
            depts = [d for d in depts if filters.name in d.name]
        return [_to_out(d) for d in depts]

    @requires_permission('iam:dept:read')
    async def get_dept(self, dept_id: DeptId, current_user: CurrentUser) -> DeptOut:
        dept = await self._load_any(dept_id)
        if not await self.dept_access_service.can_access(dept.id, current_user):
            raise PermissionDeniedException('无权访问该部门')
        return _to_out(dept)

    @requires_permission('iam:dept:read')
    async def get_dept_detail(self, dept_id: DeptId, current_user: CurrentUser) -> DeptDetailOut:
        dept = await self._load_any(dept_id)
        if not await self.dept_access_service.can_access(dept.id, current_user):
            raise PermissionDeniedException('无权访问该部门')
        audit = await self.audit_service.build(dept)
        parent_refs = (
            await self.dept_ref_service.build([dept.parent_id]) if dept.parent_id else []
        )
        leader = (await self.user_repo.get_by_ids([dept.leader_id])) if dept.leader_id else []
        leader_user = leader[0] if leader else None
        # 部门 DTO 与审计都含 created_at，先合并成 dict（后者覆盖，取值相同）再展开，避免重复关键字
        fields = {**_to_out(dept).model_dump(), **audit.model_dump()}
        return DeptDetailOut(
            **fields,
            parent=parent_refs[0] if parent_refs else None,
            leader_username=leader_user.username if leader_user else None,
            leader_nickname=leader_user.nickname if leader_user else None,
        )

    # ---------------- 写 ----------------
    @requires_permission('iam:dept:create')
    async def create_dept(self, data: CreateDeptIn, current_user: CurrentUser) -> Dept:
        async with self.in_transaction():
            parent = await self._load_available_parent(data.parent_id)
            if parent is not None and not await self.dept_access_service.can_access(parent.id, current_user):
                raise PermissionDeniedException('无权在该部门下新增')
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
            if not await self.dept_access_service.can_access(dept.id, current_user):
                raise PermissionDeniedException('无权访问该部门')
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
                if parent is not None and not await self.dept_access_service.can_access(parent.id, current_user):
                    raise PermissionDeniedException('无权移动到该部门下')
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
        """删除部门 = **级联软删整棵子树**（不允许「只删父、留子」）。

        维持不变式「父已删 ⇒ 子必删」；子树内任一部门下有用户 → 整体拒绝（守卫）。
        """
        async with self.in_transaction():
            dept = await self._load(dept_id)
            if not await self.dept_access_service.can_access(dept.id, current_user):
                raise PermissionDeniedException('无权访问该部门')
            subtree = [dept, *await self.dept_repo.get_descendants(dept.id)]
            for node in subtree:
                if await self.user_repo.exists_by_dept(node.id):
                    raise DeptHasUsersException(f'部门「{node.name}」下存在用户，不允许删除')
            parent = await self.dept_repo.get(dept.parent_id) if dept.parent_id else None
            operator = current_user.user_id
            for node in subtree:
                node.delete(operator)
                await self.dept_repo.update(node)
        await self._notify_structure_changed(parent_chain(parent))

    @requires_permission('iam:dept:delete')
    async def restore_dept(self, dept_id: DeptId, current_user: CurrentUser) -> None:
        """从回收站恢复（复用 `delete` 权限码）。

        只恢复自身；**父部门已删时拒绝**（提示先恢复父），以维持「父已删 ⇒ 子必删」。
        """
        async with self.in_transaction():
            dept = await self._load_any(dept_id)
            if not dept.is_deleted:
                raise DeptNotDeletedException('部门未被删除，无需恢复')
            if not await self.dept_access_service.can_access(
                    dept.id, current_user, include_deleted=True):
                raise PermissionDeniedException('无权访问该部门')
            parent = await self._load_restorable_parent(dept)
            dept.restore(current_user.user_id)
            await self.dept_repo.update(dept)
        await self._notify_structure_changed(parent_chain(parent))

    @requires_permission('iam:dept:hard_delete')
    async def hard_delete_dept(self, dept_id: DeptId, current_user: CurrentUser) -> None:
        """彻底删除（物理）——只允许对已软删部门做，**级联整棵子树**。

        级联清两类悬空引用：角色数据范围里对这些部门的引用（iam_role_dept 行）、
        用户（含已软删用户）的 dept_id 指向（置空）。
        """
        async with self.in_transaction():
            dept = await self._load_any(dept_id)
            if not dept.is_deleted:
                raise DeptNotDeletedException('只能彻底删除已删除的部门')
            if not await self.dept_access_service.can_access(
                    dept.id, current_user, include_deleted=True):
                raise PermissionDeniedException('无权访问该部门')
            subtree = [dept, *await self.dept_repo.get_descendants(dept.id, include_deleted=True)]
            # 不变式「父已删 ⇒ 子必删」被破坏时拒绝，避免级联杀掉未删的子树
            if any(not node.is_deleted for node in subtree):
                raise DeptNotDeletedException('子树中存在未删除的部门，无法彻底删除')
            subtree_ids = [node.id for node in subtree]
            await self.role_repo.remove_custom_depts(subtree_ids)
            await self.user_repo.clear_dept(subtree_ids)
            await self.dept_repo.hard_delete(subtree_ids)
        await self._notify_structure_changed(frozenset(subtree_ids))

    # ---------------- 内部 ----------------
    async def _load_restorable_parent(self, dept: Dept) -> Dept | None:
        """恢复前校验上级：上级不存在（已硬删）或已软删 → 拒绝，提示先恢复上级。"""
        if dept.parent_id is None:
            return None
        parent = await self.dept_repo.get(dept.parent_id, include_deleted=True)
        if parent is None or parent.is_deleted:
            raise DeptParentUnavailableException('上级部门已被删除，请先恢复上级部门')
        return parent

    async def _visible_depts(self, current_user: CurrentUser,
                             status: StatusEnum | None = None,
                             deleted: bool = False) -> list[Dept]:
        """按数据范围过滤可见部门（ALL → 不过滤）；`deleted` 缺省只看未删。"""
        depts = await self.dept_repo.get_all(status, deleted)
        spec = current_user.data_scope_spec
        if spec.kind is DataScopeEnum.ALL:
            return depts
        return [d for d in depts if d.id in spec.dept_ids]

    async def _notify_structure_changed(self, affected: set[DeptId]) -> None:
        if affected:
            await self.event_bus.publish(
                DeptStructureChanged(id=EventId.new(), affected_dept_ids=frozenset(affected)))

    async def _load(self, dept_id: DeptId) -> Dept:
        dept = await self.dept_repo.get(dept_id)  # 仓储默认不返回已删
        if dept is None:
            raise DeptNotFoundException(f'部门不存在：{dept_id}')
        return dept

    async def _load_any(self, dept_id: DeptId) -> Dept:
        """读侧加载：**不惧已删**（回收站详情要能看）。"""
        dept = await self.dept_repo.get(dept_id, include_deleted=True)
        if dept is None:
            raise DeptNotFoundException(f'部门不存在：{dept_id}')
        return dept

    async def _load_available_parent(self, parent_id: DeptId | None) -> Dept | None:
        if parent_id is None:
            return None
        parent = await self.dept_repo.get(parent_id)  # 仓储默认不返回已删
        if parent is None:
            raise DeptParentUnavailableException('上级部门不存在')
        if parent.status is not StatusEnum.ACTIVE:
            raise DeptParentUnavailableException('上级部门已停用')
        return parent

    async def _ensure_name_unique(self, parent_id: DeptId | None, name: str, exclude_id: DeptId | None) -> None:
        # 软删仍占名 → 唯一性判定显式包含已删行
        found = await self.dept_repo.get_by_parent_and_name(parent_id, name, include_deleted=True)
        if found is not None and found.id != exclude_id:
            raise DeptNameConflictException(f'同级下已存在部门：{name}')
