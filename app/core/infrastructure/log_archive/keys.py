"""归档 key 布局：{instance}/{yyyy}/{MM}/{dd}/{原始文件名}。"""
from datetime import datetime


def build_key(instance: str, mtime: float, filename: str) -> str:
    """日期取文件 mtime 的本地时间，与 loguru 时间戳一致；不解析文件名。"""
    dt = datetime.fromtimestamp(mtime)
    return f'{instance}/{dt:%Y/%m/%d}/{filename}'
