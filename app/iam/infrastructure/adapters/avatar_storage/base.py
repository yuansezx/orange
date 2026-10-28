"""S3 兼容头像存储适配器基类。

桶名由模块代码拥有（一个桶只放一种资源）；连接由 core 注入。
provider 的差异（error code / header / checksum 等）由子类覆盖。
"""
from typing import Any

from botocore.exceptions import ClientError
from future_uuid import uuid7

from app.iam.application.user.ports import AvatarStoragePort, StoredAvatar
from app.iam.domain.shared.value_objects import UserId

AVATAR_BUCKET = 'orange-avatars'

_OBJECT_NOT_FOUND = {'404', 'NoSuchKey', 'NotFound'}
_BUCKET_NOT_FOUND = {'404', 'NoSuchBucket', 'NotFound'}


def _error_code(exc: ClientError) -> str:
    return exc.response.get('Error', {}).get('Code', '')


class AvatarStorageS3Adapter(AvatarStoragePort):
    bucket = AVATAR_BUCKET

    def __init__(self, client: Any):
        self._client = client

    async def ensure_ready(self) -> None:
        try:
            await self._client.head_bucket(Bucket=self.bucket)
            return
        except ClientError as exc:
            if _error_code(exc) not in _BUCKET_NOT_FOUND:
                raise
        try:
            await self._client.create_bucket(Bucket=self.bucket)
        except ClientError as exc:
            if _error_code(exc) != 'BucketAlreadyOwnedByYou':
                raise

    async def save(self, user_id: UserId, data: bytes, content_type: str) -> str:
        key = f'users/{user_id.value}/avatar/{uuid7()}'
        await self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return key

    async def load(self, key: str) -> StoredAvatar | None:
        try:
            response = await self._client.get_object(Bucket=self.bucket, Key=key)
        except ClientError as exc:
            if _error_code(exc) in _OBJECT_NOT_FOUND:
                return None
            raise
        body = response['Body']
        try:
            data = await body.read()
        finally:
            body.close()
        return StoredAvatar(
            data=data,
            content_type=response.get('ContentType') or 'application/octet-stream',
        )

    async def delete(self, key: str) -> None:
        await self._client.delete_object(Bucket=self.bucket, Key=key)
