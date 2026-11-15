"""monitor 应用层端口。"""
from abc import ABC, abstractmethod

from app.monitor.application.common.dto import CurrentUser


class AuthenticationPort(ABC):
    """token → 当前用户；实现方负责对接 iam 并翻译异常。"""

    @abstractmethod
    async def authenticate(self, token: str) -> CurrentUser: ...


class SystemInfoPort(ABC):
    """平台与模块的版本信息（只读）。"""

    @abstractmethod
    def get_platform_version(self) -> str: ...

    @abstractmethod
    def get_module_versions(self) -> dict[str, str]:
        """返回**自带版本声明**的模块（非平台模块）；平台内置模块不出现。"""
