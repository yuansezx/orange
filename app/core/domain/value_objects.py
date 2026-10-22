from typing import Self
from uuid import UUID

from future_uuid import uuid7
from pydantic import ConfigDict, RootModel, model_validator


class SingleValueObject[T](RootModel[T]):
    """单值值对象基类：不可变，pydantic 下按**裸值**出入（OpenAPI 里也展示为裸值）。

    - 校验：裸值 / 同类型实例 → 构造；
    - 序列化：裸值（嵌套进实体 / 响应模型时同样是裸值）。

    **多字段（结构化）VO 不套本基类**，用 frozen `BaseModel`。
    """
    model_config = ConfigDict(frozen=True)

    @model_validator(mode='before')
    @classmethod
    def _unwrap_instance(cls, v):
        return v.root if isinstance(v, cls) else v

    @property
    def value(self) -> T:
        return self.root

    def __str__(self) -> str:
        return str(self.root)


class BaseEntityId(SingleValueObject[UUID]):
    """实体 ID 值对象：包装 UUID（str 入口由 pydantic 自动转 UUID）。"""

    @classmethod
    def new(cls) -> Self:
        return cls(uuid7())


class EventId(BaseEntityId):
    pass
