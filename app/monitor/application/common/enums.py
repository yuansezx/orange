"""monitor 应用层的本地枚举（镜像 iam 公开契约中的取值）。"""
from enum import Enum


class UserTypeEnum(str, Enum):
    """用户类型；取值与 iam 的公开契约保持一致。"""
    ADMIN_CREATED = 'admin_created'
    SELF_REGISTERED = 'self_registered'
    SYSTEM = 'system'
    SUPER_ADMIN = 'super_admin'
