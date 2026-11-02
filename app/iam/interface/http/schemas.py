"""iam 模块级共享 HTTP schema。"""
from app.iam.application.common.dto import UpdateStatusIn


class UpdateStatusReq(UpdateStatusIn):
    """启用/停用请求——线格式同 DTO。"""
