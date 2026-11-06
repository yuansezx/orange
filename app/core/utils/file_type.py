"""文件类型识别（libmagic / 容器结构）。

纯计算工具，不做 IO / 不套 Port；Windows 由 python-magic-bin 提供 libmagic，
Linux 部署需安装系统包 `libmagic1`。
"""
import zipfile
from io import BytesIO

import magic


def detect_mime_type(data: bytes) -> str:
    """按文件内容识别 MIME；不信任客户端声明的 Content-Type。"""
    return magic.from_buffer(data, mime=True)


def is_zip_file(data: bytes) -> bool:
    """是否是有效的 zip；magic 对容器格式识别不稳定，这里按结构判断。"""
    return zipfile.is_zipfile(BytesIO(data))


def is_xlsx_file(data: bytes) -> bool:
    """是否是有效的 xlsx：是 zip 且包含工作簿入口 `xl/workbook.xml`。

    不能用 magic 判 xlsx——它本质是 zip，libmagic 常报 application/zip。
    """
    if not is_zip_file(data):
        return False
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            return 'xl/workbook.xml' in archive.namelist()
    except zipfile.BadZipFile:
        return False
