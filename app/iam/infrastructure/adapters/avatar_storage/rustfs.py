"""RustFS 头像存储适配器。"""
from app.iam.infrastructure.adapters.avatar_storage.base import AvatarStorageS3Adapter


class AvatarStorageS3RustFSAdapter(AvatarStorageS3Adapter):
    """RustFS 差异点收口处（目前无；error code / checksum 等兼容处理放这里）。"""
