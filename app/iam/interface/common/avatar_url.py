"""头像 URL 的唯一拼装点：HTTP 与公开 Python API 共用。"""
from urllib.parse import quote

from app.iam.domain.shared.value_objects import UserId


def build_avatar_url(user_id: UserId, avatar_key: str | None) -> str | None:
    """相对 URL（带 key 末段作版本号）；由前端经同一 origin 访问。"""
    if not avatar_key:
        return None
    version = quote(avatar_key.rsplit('/', 1)[-1], safe='')
    return f'/api/iam/users/{user_id}/avatar?v={version}'
