from pydantic import BaseModel


class ModuleVersionOut(BaseModel):
    name: str
    version: str


class SystemVersionsOut(BaseModel):
    platform_version: str
    modules: list[ModuleVersionOut]
