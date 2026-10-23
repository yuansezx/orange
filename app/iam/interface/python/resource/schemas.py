"""资源/权限目录注册的公开 schema（接口层契约）。

当前字段与应用层 DTO 一致，用空子类留出契约缝隙；以后公开面需要独立演进时，
在这里改字段并补映射，消费方不受应用层 DTO 变化直接影响。
"""
from app.iam.application.resource.dto import (
    RegisterPermissionIn as _RegisterPermissionIn,
    RegisterResourceIn as _RegisterResourceIn,
)


class RegisterPermissionReq(_RegisterPermissionIn):
    """公开 API 的权限声明入参。"""


class RegisterResourceReq(_RegisterResourceIn):
    """公开 API 的资源声明入参。"""
