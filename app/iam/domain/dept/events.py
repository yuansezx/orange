from pydantic import Field

from app.core.domain.events import BaseEvent
from app.core.domain.value_objects import EventId
from app.iam.domain.shared.value_objects import DeptId


class DeptStructureChanged(BaseEvent):
    """部门结构变更（新增 / 移动 / 删除）——影响 DEPT_AND_CHILD 的部门展开。

    `affected_dept_ids` = 变动部门在**旧/新父祖先链**上的那批部门；自身部门落在其中的
    DEPT_AND_CHILD 用户，其缓存的数据范围展开会变，需失效快照。
    """
    id: EventId = Field(default_factory=EventId.new)
    affected_dept_ids: frozenset[DeptId]
