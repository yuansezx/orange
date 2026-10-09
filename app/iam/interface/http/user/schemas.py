"""接口层 schema 可直接引用 domain 值对象（UserId / Phone / Email）作字段类型。

值对象经 `SingleValueObject` 统一处理：校验接受 裸值 / `{"value": ...}` / 实例，
序列化出裸值，OpenAPI 展示为 `string`（id 带 `format: uuid`）。故无需重复写 pattern。
"""
