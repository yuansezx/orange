"""文件类型识别（libmagic / 容器结构）。

纯计算工具，不做 IO / 不套 Port；Windows 由 python-magic-bin 提供 libmagic，
Linux 部署需安装系统包 `libmagic1`。
"""
import zipfile
from io import BytesIO

import magic


XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
ZIP_MIME = 'application/zip'


def detect_mime_type(data: bytes) -> str:
    """按文件内容识别 MIME；不信任客户端声明的 Content-Type。

    容器格式优先按结构判断（libmagic 对 xlsx 常只报 application/zip），
    其余交给 libmagic。调用方只关心返回值，不需要知道判定顺序。
    """
    if is_xlsx_file(data):
        return XLSX_MIME
    if is_zip_file(data):
        return ZIP_MIME
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
