from dataclasses import dataclass
from typing import Generic, Self, TypeVar
from uuid import UUID

from future_uuid import uuid7
from pydantic_core import core_schema

T = TypeVar('T')


@dataclass(frozen=True)
class SingleValueObject(Generic[T]):
    """单值值对象基类：pydantic 下按**裸值**出入（OpenAPI 里也展示为裸值）。

    - 校验：裸值 / `{"value": ...}` / 同类型实例 → 构造（`__post_init__` 负责校验与规整）；
    - 序列化：`str(self)`（默认 `str(self.value)`，子类可覆盖 `__str__`）。

    **多字段（结构化）VO 不套本基类**，交给 pydantic 默认按对象序列化。
    """
    value: T

    @classmethod
    def _from_wire(cls, v):
        if isinstance(v, cls):
            return v
        if isinstance(v, dict):
            return cls(v['value'])
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_plain_validator_function(
            cls._from_wire,
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        # plain validator 默认不生成 JSON schema（会让 /openapi.json 报错）；显式声明为字符串。
        return handler(core_schema.str_schema())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class BaseEntityId(SingleValueObject[UUID]):
    """实体 ID 值对象：包装 UUID；构造时把 str 强制转成 UUID（JWT/路径参数等入口）。"""

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            object.__setattr__(self, 'value', UUID(self.value))

    @classmethod
    def new(cls) -> Self:
        return cls(value=uuid7())

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        return handler(core_schema.uuid_schema())  # OpenAPI 里展示为 {type: string, format: uuid}


@dataclass(frozen=True)
class EventId(BaseEntityId):
    pass
