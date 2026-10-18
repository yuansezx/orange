from datetime import datetime

from pydantic import BaseModel, Field

from app.iam.application.common.dto import AuditOut, DeptRefOut
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, Email, Phone, UserId


class CreateDeptIn(BaseModel):
    name: str
    parent_id: DeptId | None = None            # None = 顶级部门
    leader_id: UserId | None = None
    email: Email | None = None
    phone: Phone | None = None
    description: str | None = None


class UpdateDeptIn(BaseModel):
    """部门更新——用 `model_fields_set` 区分「未传」与「显式传 null（移到顶级）」。"""
    id: DeptId
    name: str | None = None
    parent_id: DeptId | None = None
    leader_id: UserId | None = None
    email: Email | None = None
    phone: Phone | None = None
    description: str | None = None
    status: StatusEnum | None = None


class GetDeptsIn(BaseModel):
    name: str | None = None                    # 部门名模糊
    status: StatusEnum | None = None           # 业务状态（ACTIVE/DISABLED）
    deleted: bool = False                      # True = 只看回收站


class DeptOut(BaseModel):
    id: DeptId
    name: str
    parent_id: DeptId | None = None
    leader_id: UserId | None = None
    email: Email | None = None
    phone: Phone | None = None
    status: StatusEnum
    description: str | None = None
    created_at: datetime


class DeptTreeNode(DeptOut):
    children: list['DeptTreeNode'] = Field(default_factory=list)


class DeptDetailOut(DeptOut, AuditOut):
    """部门详情——数据字段 + 审计（平铺）+ 上级部门引用 + 负责人（用户名+昵称）。"""
    parent: DeptRefOut | None = None
    leader_username: str | None = None
    leader_nickname: str | None = None
