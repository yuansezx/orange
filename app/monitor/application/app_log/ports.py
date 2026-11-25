"""应用日志端口：归档存储读取、本地实时 tail、core 归档触发。

端口特有的技术中立异常放这里（基础设施只抛中立异常，应用层翻译成业务异常）。
"""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import date

from app.core.exceptions import InfrastructureBaseException
from app.monitor.application.app_log.dto import AppLogFileOut


class AppLogKeyInvalidException(InfrastructureBaseException):
    """归档 key 不符合布局或不属于本实例。"""


class AppLogObjectNotFoundException(InfrastructureBaseException):
    """归档对象不存在。"""


class AppLogStorePort(ABC):
    """读取 core 写出的归档应用日志（对象存储）。"""

    @abstractmethod
    async def list_files(self, date_from: date | None,
                         date_to: date | None) -> list[AppLogFileOut]: ...

    @abstractmethod
    async def read_file(self, key: str) -> bytes: ...


class AppLogTailPort(ABC):
    """实时读取本地活跃日志文件（SSE 数据行）。"""

    @abstractmethod
    def stream(self, file: str) -> AsyncIterator[str]: ...


class AppLogArchiveTriggerPort(ABC):
    """手动触发 core 的归档任务；未启用返回 False。"""

    @abstractmethod
    def trigger(self) -> bool: ...
