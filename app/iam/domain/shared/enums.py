from enum import Enum

# python的枚举类，已有成员则不可继承，与ddd的“共享概念但局部可扩展”有些摩擦
class StatusEnum(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"  # 用来实现回收站功能，软删除只改status，真删除才清理关系


class DataScopeEnum(str, Enum):
    """数据范围（数据权限）——某用户能看/操作哪些数据。"""
    ALL = "all"                        # 不限（超管）
    DEPT = "dept"                      # 本部门
    DEPT_AND_CHILD = "dept_and_child"  # 本部门及子部门
    CUSTOM = "custom"                  # 指定部门（custom_dept_ids）
    SELF = "self"                      # 仅本人
