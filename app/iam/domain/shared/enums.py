from enum import Enum

# python的枚举类，已有成员则不可继承，与ddd的“共享概念但局部可扩展”有些摩擦
class StatusEnum(str, Enum):
    """业务可用性状态。**不含「已删除」**——删除是正交维度，以 `deleted_at` 判别。"""
    ACTIVE = "active"
    DISABLED = "disabled"


class AuthMethodEnum(str, Enum):
    """单次认证的来源 / 凭据类型（审计与安全策略用；**不是用户属性**）。"""
    PASSWORD = "password"  # 登录事件
    SESSION = "session"    # 第一方 Bearer 会话
    API_KEY = "api_key"    # 用户 API Key（PAT）
    OAUTH = "oauth"        # 第三方委派（预留）


class SortOrderEnum(str, Enum):
    """列表排序方向（单字段排序用）。"""
    ASC = "asc"
    DESC = "desc"


class DataScopeEnum(str, Enum):
    """数据范围（数据权限）——某用户能看/操作哪些数据。"""
    ALL = "all"                        # 不限（超管）
    DEPT = "dept"                      # 本部门
    DEPT_AND_CHILD = "dept_and_child"  # 本部门及子部门
    CUSTOM = "custom"                  # 指定部门（custom_dept_ids）
    SELF = "self"                      # 仅本人
