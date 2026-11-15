"""版本信息适配器：平台版本取 core 配置，模块版本读模块自己的 pyproject。

非平台模块按约定自带 `app/<module>/pyproject.toml`；平台内置模块（iam/monitor）
属于根发行版，没有独立 pyproject，因此不出现在模块版本列表里。
"""
import tomllib
from importlib import import_module
from pathlib import Path

from loguru import logger

from app.core.infrastructure.settings import CORE_SETTINGS
from app.monitor.application.common.ports import SystemInfoPort


class SystemInfoAdapter(SystemInfoPort):

    def get_platform_version(self) -> str:
        return CORE_SETTINGS.app_version

    def get_module_versions(self) -> dict[str, str]:
        versions: dict[str, str] = {}
        for name in CORE_SETTINGS.modules:
            version = _read_module_version(name)
            if version is not None:
                versions[name] = version
        return versions


def _read_module_version(name: str) -> str | None:
    path = f'app.{name}'
    try:
        package = import_module(path)
    except ModuleNotFoundError as exc:
        if exc.name == path:
            logger.warning('模块 {} 未安装，无法读取版本', name)
            return None
        raise
    package_file = getattr(package, '__file__', None)
    if package_file is None:
        return None
    pyproject = Path(package_file).with_name('pyproject.toml')
    try:
        with pyproject.open('rb') as f:
            return tomllib.load(f)['project']['version']
    except (OSError, KeyError):
        return None
