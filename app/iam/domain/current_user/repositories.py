from __future__ import annotations  # 方法名 set 会遮蔽内建 set，注解须延迟求值

from abc import ABC, abstractmethod

from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import UserId


class CurrentUserRepository(ABC):
    """当前用户缓存（Redis）。set 写入并设 TTL；get 未命中返回 None；evict 淘汰。"""

    @abstractmethod
    async def set(self, current_user: CurrentUser) -> None: ...

    @abstractmethod
    async def get(self, user_id: UserId) -> CurrentUser | None: ...

    @abstractmethod
    async def evict(self, user_ids: UserId | list[UserId] | set[UserId]) -> None: ...
