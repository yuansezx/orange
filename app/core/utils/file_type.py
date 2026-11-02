"""文件类型识别（libmagic）。

纯计算工具，不做 IO / 不套 Port；Windows 由 python-magic-bin 提供 libmagic，
Linux 部署需安装系统包 `libmagic1`。
"""
import magic


def detect_mime_type(data: bytes) -> str:
    """按文件内容识别 MIME；不信任客户端声明的 Content-Type。"""
    return magic.from_buffer(data, mime=True)
