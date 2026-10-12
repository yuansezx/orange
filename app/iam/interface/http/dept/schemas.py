"""部门 HTTP schema（Req / Resp）。

字段直接用 domain 值对象（DeptId / UserId / Email / Phone），经 `SingleValueObject`
统一裸值出入、OpenAPI 展示为 string（id 带 format: uuid）。
"""
from pydantic import BaseModel

from app.iam.application.dept.dto import CreateDeptIn, DeptOut, DeptTreeNode, GetDeptsIn
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, Email, Phone, UserId


class CreateDeptReq(CreateDeptIn):
    """创建部门请求——线格式同 DTO。"""


class UpdateDeptReq(BaseModel):
    """更新部门请求——id 来自路径，故不含 id；可选字段，用 exclude_unset 区分未传/传 null。"""
    name: str | None = None
    parent_id: DeptId | None = None
    leader_id: UserId | None = None
    email: Email | None = None
    phone: Phone | None = None
    description: str | None = None
    status: StatusEnum | None = None


class GetDeptsReq(GetDeptsIn):
    """部门列表查询参数——线格式同 DTO。"""


class DeptResp(DeptOut):
    """部门响应——线格式同 DTO。"""


class DeptTreeNodeResp(DeptTreeNode):
    """部门树节点响应。"""
