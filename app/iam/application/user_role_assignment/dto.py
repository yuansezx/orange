from pydantic import BaseModel, Field

from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import UserId
from app.iam.domain.user.enums import UserTypeEnum


class GetRoleCandidatesIn(BaseModel):
    """角色成员候选查询：复用用户检索能力（数据范围在仓储侧过滤）。"""
    keyword: str | None = None
    status: StatusEnum | None = None
    user_type: UserTypeEnum | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class RoleCandidateUserOut(BaseModel):
    """候选用户 + 是否已持有该角色（未删除分配即为 True）。"""
    id: UserId
    username: str
    nickname: str
    user_type: UserTypeEnum
    status: StatusEnum
    selected: bool
