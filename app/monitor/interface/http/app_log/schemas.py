"""应用日志 HTTP schema。"""
from app.monitor.application.app_log.dto import AppLogFileOut, GetAppLogsIn


class GetAppLogsReq(GetAppLogsIn):
    """应用日志列表查询参数（线格式同 DTO）。"""


class AppLogFileResp(AppLogFileOut):
    """归档应用日志文件响应。"""
