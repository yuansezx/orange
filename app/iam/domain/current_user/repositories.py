from abc import ABC

from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import UserId


class CurrentUserRepository(ABC):

    async def set(self, current_user: CurrentUser) -> None: ...

    async def get(self, user_id: UserId) -> CurrentUser: ...

    async def delete(self, user_ids: UserId | list[UserId] | set[UserId]) -> None: ...
