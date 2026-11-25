"""应用日志应用服务：列表 / 查看 / 下载 / 实时 tail / 手动触发归档。"""
from collections.abc import AsyncIterator

from app.monitor.application.app_log.dto import AppLogFileOut, GetAppLogsIn
from app.monitor.application.app_log.exceptions import (
    MonitorAppLogArchiveDisabledException,
    MonitorAppLogFileInvalidException,
    MonitorAppLogFileNotFoundException,
)
from app.monitor.application.app_log.ports import (
    AppLogArchiveTriggerPort,
    AppLogKeyInvalidException,
    AppLogObjectNotFoundException,
    AppLogStorePort,
    AppLogTailPort,
)
from app.monitor.application.common.decorators import requires_permission
from app.monitor.application.common.dto import CurrentUser

_TAIL_FILES = frozenset({'app', 'error'})


class AppLogApplicationService:
    def __init__(self, *, store: AppLogStorePort, tail: AppLogTailPort,
                 trigger: AppLogArchiveTriggerPort) -> None:
        self._store = store
        self._tail = tail
        self._trigger = trigger

    @requires_permission('monitor:app_log:read')
    async def list_files(self, data: GetAppLogsIn,
                         current_user: CurrentUser) -> list[AppLogFileOut]:
        return await self._store.list_files(data.date_from, data.date_to)

    @requires_permission('monitor:app_log:read')
    async def read_file(self, key: str, current_user: CurrentUser) -> bytes:
        try:
            return await self._store.read_file(key)
        except AppLogKeyInvalidException as exc:
            raise MonitorAppLogFileInvalidException('非法的日志 key') from exc
        except AppLogObjectNotFoundException as exc:
            raise MonitorAppLogFileNotFoundException('日志文件不存在') from exc

    @requires_permission('monitor:app_log:read')
    async def stream(self, file: str,
                     current_user: CurrentUser) -> AsyncIterator[str]:
        if file not in _TAIL_FILES:
            raise MonitorAppLogFileInvalidException('文件必须是 app 或 error')
        return self._tail.stream(file)

    @requires_permission('monitor:app_log:archive')
    async def trigger_archive(self, current_user: CurrentUser) -> None:
        if not self._trigger.trigger():
            raise MonitorAppLogArchiveDisabledException('日志归档未启用')
