from pydantic import BaseModel


class HealthResp(BaseModel):
    """健康检查响应。"""
    status: str
    module: str
    app_name: str
    app_version: str
