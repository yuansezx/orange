from enum import Enum


class DataScopeEnum(str, Enum):
    ALL = "all"
    DEPT = "dept"
    DEPT_AND_CHILD = "dept_and_child"
    CUSTOM = "custom"
    SELF = "self"
