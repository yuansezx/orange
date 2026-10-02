from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeAlias


class TransactionContext(ABC):

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    # @abstractmethod
    # async def commit(self): ...
    #
    # @abstractmethod
    # async def rollback(self): ...


InTransactionType: TypeAlias = (Callable[[], TransactionContext])
