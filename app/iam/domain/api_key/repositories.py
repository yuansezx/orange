from abc import abstractmethod
from datetime import datetime

from app.core.domain.repositories import BaseRepository
from app.iam.domain.api_key.entities import ApiKey
from app.iam.domain.shared.enums import StatusEnum
from app.iam.domain.shared.value_objects import ApiKeyId, UserId


class ApiKeyRepository(BaseRepository[ApiKeyId, ApiKey]):
    """API Key 仓储接口。

    key 是用户凭据（PAT），生命周期独立于用户；权限/数据范围不落派生值，
    认证时由用户快照与 key 的选择项合成。
    """

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str, *,
                                include_deleted: bool = False) -> ApiKey | None:
        """按整串 token 的摘要查（认证路径）；默认不返回已吊销的 key。"""
        ...

    @abstractmethod
    async def get_all(self, user_id: UserId | None = None, status: StatusEnum | None = None,
                      deleted: bool = False) -> list[ApiKey]:
        """`user_id=None` 取全部用户（管理端）；缺省只看未吊销，`deleted=True` 只看已吊销；
        `status` 只筛启停。用户自助列表传 `user_id`，数量通常很少，不分页。"""
        ...

    @abstractmethod
    async def update_last_used(self, api_key_id: ApiKeyId, used_at: datetime) -> None:
        """只更新最近使用时间（节流写）；不盖 updated_at / updated_by。"""
        ...

    @abstractmethod
    async def hard_delete_by_user(self, user_id: UserId) -> int:
        """物理清理：用户彻底删除时移除其全部 key（应用层级联，避免悬空凭据）。"""
        ...
