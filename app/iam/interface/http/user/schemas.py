"""
接口层 schema 可直接引用 domain 值对象（Phone / Email）作为字段类型，
pydantic 自动调 __init__/__post_init__ 做校验，无需重复写 pattern。
如需 API 文档展示约束信息，后续再补 Field(pattern=...)。
"""
