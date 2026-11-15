from pydantic import BaseModel


class ModuleVersionResp(BaseModel):
    name: str
    version: str


class SystemVersionsResp(BaseModel):
    platform_version: str
    modules: list[ModuleVersionResp]
