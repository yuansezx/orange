from datetime import datetime

from pydantic import BaseModel

from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import DeptId, RoleSummary, UserId


class UpdateStatusIn(BaseModel):
    """启用/停用——统一状态变更入口的请求体。"""
    status: StatusEnum


class EffectivePermissions(BaseModel):
    """某用户「有效」的角色与权限（逐级按 ACTIVE 过滤后的结果）。"""
    roles: frozenset[RoleSummary]
    permission_codes: frozenset[str]  # module:resource:action


class OperatorOut(BaseModel):
    """审计操作人。**id 来自实体上的审计列**，行不存在（已硬删）时名字为 None。"""
    id: UserId
    username: str | None = None
    nickname: str | None = None


class AuditOut(BaseModel):
    """审计**操作人**；生命周期时间属于数据 DTO，不在此重复。

    字段为 None = 该操作未发生；对象在但名字为 None = 操作人已被硬删。
    """
    created_by: OperatorOut | None = None
    updated_by: OperatorOut | None = None
    deleted_by: OperatorOut | None = None


class DeptRefOut(BaseModel):
    """部门引用（读侧展示）：id + 名称 + 层级路径（根→自身）。"""
    id: DeptId
    name: str
    path: str
