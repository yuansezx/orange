"""monitor 应用层端口。"""
from abc import ABC, abstractmethod

from app.monitor.application.common.dto import CurrentUser


class AuthenticationPort(ABC):
    """token → 当前用户；实现方负责对接 iam 并翻译异常。"""

    @abstractmethod
    async def authenticate(self, token: str) -> CurrentUser: ...
