"""iam 对外 Python API 的部门 schema。"""
from uuid import UUID

from pydantic import BaseModel


class DeptRefResp(BaseModel):
    """批量部门引用（供其他模块展示所属部门）。"""
    id: UUID
    name: str
