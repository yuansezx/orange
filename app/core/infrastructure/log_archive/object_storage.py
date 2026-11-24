"""对象存储 sink：专用 logs 桶，桶名由代码拥有；连接由配置选择。"""
from typing import Any

from botocore.exceptions import ClientError

from app.core.infrastructure.object_storage import get_object_storage_client

LOG_BUCKET = 'orange-logs'

_BUCKET_NOT_FOUND = {'404', 'NoSuchBucket', 'NotFound'}


class ObjectStorageLogSink:
    def __init__(self, connection: str = 'default') -> None:
        self._client: Any = get_object_storage_client(connection)
        self._bucket = LOG_BUCKET

    async def ensure_ready(self) -> None:
        try:
            await self._client.head_bucket(Bucket=self._bucket)
        except ClientError as exc:
            code = exc.response.get('Error', {}).get('Code', '')
            if code not in _BUCKET_NOT_FOUND:
                raise
            await self._client.create_bucket(Bucket=self._bucket)

    async def put(self, key: str, data: bytes) -> None:
        await self._client.put_object(Bucket=self._bucket, Key=key, Body=data)
