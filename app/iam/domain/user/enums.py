from enum import Enum


class UserType(str, Enum):
    ADMIN_CREATED = "admin_created"
    SELF_REGISTERED = "self_registered"
    DEMO = "demo"
    SYSTEM = "system"
    SUPER_ADMIN = "super_admin"  # “逃生舱”，仅初始化时创建首个用户使用，不可滥用
