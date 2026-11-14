from pydantic import Field

from app.core.domain.events import BaseEvent
from app.core.domain.value_objects import EventId
from app.iam.domain.shared.value_objects import DeptId


class DeptStructureChanged(BaseEvent):
    """部门变更（结构增/移/删，或快照可见资料如重命名）。

    `affected_dept_ids` 是**需要重建快照的部门集合**：自身部门落在其中的用户全部失效。
    包含旧/新父祖先链的对称差（DEPT_AND_CHILD 展开会变）、被移动部门及其子树
    （`dept.ancestors` 会变），以及被重命名部门本身（`dept.name` 进了快照）。
    """
    id: EventId = Field(default_factory=EventId.new)
    affected_dept_ids: frozenset[DeptId]
