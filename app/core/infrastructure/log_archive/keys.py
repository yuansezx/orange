"""归档 key 布局：{instance}/{yyyy}/{MM}/{dd}/{原始文件名}。"""
from datetime import date, datetime


def build_key(instance: str, mtime: float, filename: str) -> str:
    """日期取文件 mtime 的本地时间，与 loguru 时间戳一致；不解析文件名。"""
    dt = datetime.fromtimestamp(mtime)
    return f'{instance}/{dt:%Y/%m/%d}/{filename}'


def parse_key(key: str) -> tuple[str, date, str] | None:
    """解析归档 key；格式不符返回 None。"""
    parts = key.split('/', 4)
    if len(parts) != 5:
        return None
    instance, yyyy, mm, dd, filename = parts
    if not instance or not filename:
        return None
    try:
        log_date = date(int(yyyy), int(mm), int(dd))
    except ValueError:
        return None
    return instance, log_date, filename
