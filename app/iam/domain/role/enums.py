from enum import Enum


class DataScope(str, Enum):
    ALL = "all"
    DEPT = "dept"
    DEPT_AND_CHILD = "dept_and_child"
    CUSTOM = "custom"
    SELF = "self"
