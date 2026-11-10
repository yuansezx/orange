"""API Key HTTP schema。"""
from app.iam.application.api_key.dto import (
    ApiKeyAdminOut,
    ApiKeyCreatedOut,
    ApiKeyOut,
    CreateApiKeyIn,
    GetApiKeysIn,
    ResourceCandidateOut,
    UpdateApiKeyIn,
)


class CreateApiKeyReq(CreateApiKeyIn):
    """创建请求（线格式同 DTO）。"""


class UpdateApiKeyReq(UpdateApiKeyIn):
    """全量更新请求（线格式同 DTO）。"""


class GetApiKeysReq(GetApiKeysIn):
    """管理端列表查询参数。"""


class ApiKeyResp(ApiKeyOut):
    """API Key 响应（不含明文）。"""


class ApiKeyCreatedResp(ApiKeyCreatedOut):
    """创建响应（明文 token 只出现一次）。"""


class ApiKeyAdminResp(ApiKeyAdminOut):
    """管理端 API Key 响应（含所属用户）。"""


class ScopeCandidateResp(ResourceCandidateOut):
    """可授予权限候选（按资源分组）。"""
