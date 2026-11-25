"""手动触发日志归档：调用 core 的公开门面（模块 infrastructure 依赖 core 同层门面）。"""
from app.core import trigger_log_archive
from app.monitor.application.app_log.ports import AppLogArchiveTriggerPort


class AppLogTriggerAdapter(AppLogArchiveTriggerPort):
    def trigger(self) -> bool:
        return trigger_log_archive()
