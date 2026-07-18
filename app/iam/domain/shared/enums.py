from enum import Enum

# python的枚举类，已有成员则不可继承，与ddd的“共享概念但局部可扩展”有些摩擦
class Status(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"  # 用来实现回收站功能，软删除只改status，真删除才清理关系
