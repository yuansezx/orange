from loguru import logger

from app.iam.domain.current_user.repositories import CurrentUserRepository
from app.iam.domain.shared.value_objects import UserId


async def clear_current_users_cache(user_ids: UserId | list[UserId] | set[UserId],current_user_repo: CurrentUserRepository):
    try:
        await current_user_repo.evict(user_ids)
    except Exception as e:
        logger.error(e)