from app.monitor.application.common.decorators import requires_permission
from app.monitor.application.common.dto import CurrentUser
from app.monitor.application.common.ports import SystemInfoPort
from app.monitor.application.system.dto import ModuleVersionOut, SystemVersionsOut


class SystemInfoApplicationService:
    """平台/模块版本信息（只读）。"""

    def __init__(self, system_info: SystemInfoPort) -> None:
        self.system_info = system_info

    @requires_permission('monitor:system:read')
    async def get_versions(self, current_user: CurrentUser) -> SystemVersionsOut:
        versions = self.system_info.get_module_versions()
        return SystemVersionsOut(
            platform_version=self.system_info.get_platform_version(),
            modules=[ModuleVersionOut(name=name, version=version)
                     for name, version in sorted(versions.items())],
        )
