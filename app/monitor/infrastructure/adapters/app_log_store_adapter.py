"""应用日志归档存储适配器：从 core 的专用 logs 桶读取冷文件。

key 布局与桶名由 core 拥有；这里只做读取与 key 校验。
"""
from datetime import date
from typing import Any

from botocore.exceptions import ClientError

from app.core.infrastructure.log_archive.keys import parse_key
from app.core.infrastructure.log_archive.object_storage import LOG_BUCKET
from app.core.infrastructure.object_storage import get_object_storage_client
from app.monitor.application.app_log.dto import AppLogFileOut
from app.monitor.application.app_log.ports import (
    AppLogKeyInvalidException,
    AppLogObjectNotFoundException,
    AppLogStorePort,
)

_NOT_FOUND = {'404', 'NoSuchBucket', 'NoSuchKey', 'NotFound'}


def _error_code(exc: ClientError) -> str:
    return exc.response.get('Error', {}).get('Code', '')


class AppLogStoreAdapter(AppLogStorePort):
    def __init__(self, *, connection: str, instance: str) -> None:
        self._client: Any = get_object_storage_client(connection)
        self._instance = instance

    async def list_files(self, date_from: date | None,
                         date_to: date | None) -> list[AppLogFileOut]:
        prefix = f'{self._instance}/'
        items: list[AppLogFileOut] = []
        token: str | None = None
        while True:
            kwargs: dict[str, Any] = {'Bucket': LOG_BUCKET, 'Prefix': prefix}
            if token is not None:
                kwargs['ContinuationToken'] = token
            try:
                resp = await self._client.list_objects_v2(**kwargs)
            except ClientError as exc:
                if _error_code(exc) in _NOT_FOUND:
                    return []
                raise
            for obj in resp.get('Contents', []):
                parsed = parse_key(obj['Key'])
                if parsed is None:
                    continue
                instance, log_date, filename = parsed
                if instance != self._instance:
                    continue
                if date_from is not None and log_date < date_from:
                    continue
                if date_to is not None and log_date > date_to:
                    continue
                items.append(AppLogFileOut(
                    key=obj['Key'],
                    filename=filename,
                    instance=instance,
                    log_date=log_date,
                    size=obj['Size'],
                    last_modified=obj['LastModified'],
                ))
            if not resp.get('IsTruncated'):
                break
            token = resp.get('NextContinuationToken')
            if token is None:
                break
        items.sort(key=lambda item: (item.log_date, item.filename), reverse=True)
        return items

    async def read_file(self, key: str) -> bytes:
        parsed = parse_key(key)
        if parsed is None or parsed[0] != self._instance:
            raise AppLogKeyInvalidException(f'非法的日志 key：{key}')
        try:
            resp = await self._client.get_object(Bucket=LOG_BUCKET, Key=key)
        except ClientError as exc:
            if _error_code(exc) in _NOT_FOUND:
                raise AppLogObjectNotFoundException(key) from exc
            raise
        async with resp['Body'] as body:
            return await body.read()
