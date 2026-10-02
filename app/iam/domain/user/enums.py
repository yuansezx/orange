from enum import Enum


class UserTypeEnum(str, Enum):
    ADMIN_CREATED = "admin_created" # 管理员创建的
    SELF_REGISTERED = "self_registered" # 自己注册
    SYSTEM = "system" # 系统用户
    SUPER_ADMIN = "super_admin"  # “逃生舱”，仅初始化时创建首个用户使用，不可滥用
