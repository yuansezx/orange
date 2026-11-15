"""部门公开 API：批量展示引用。"""
from uuid import UUID

from app.iam.domain.shared.value_objects import DeptId
from app.iam.interface.dependences import get_dept_repo
from app.iam.interface.python.dept.schemas import DeptRefResp


async def get_dept_refs(dept_ids: list[UUID]) -> list[DeptRefResp]:
    """批量按 id 取部门展示引用；含软删部门，硬删部门自然缺失。"""
    if not dept_ids:
        return []
    depts = await get_dept_repo().get_by_ids(
        [DeptId(dept_id) for dept_id in dept_ids], include_deleted=True)
    return [DeptRefResp(id=dept.id.value, name=dept.name) for dept in depts]
