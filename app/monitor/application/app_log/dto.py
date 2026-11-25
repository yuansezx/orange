"""应用日志应用层 DTO。"""
from datetime import date, datetime

from pydantic import BaseModel


class GetAppLogsIn(BaseModel):
    """归档应用日志列表查询。"""
    date_from: date | None = None
    date_to: date | None = None


class AppLogFileOut(BaseModel):
    """归档应用日志文件（对象存储里的一个冷文件）。"""
    key: str
    filename: str
    instance: str
    log_date: date
    size: int
    last_modified: datetime
