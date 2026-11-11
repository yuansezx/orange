from enum import Enum


class RoleSortFieldEnum(str, Enum):
    """角色列表允许排序的字段（白名单）。"""
    CODE = "code"
    NAME = "name"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
