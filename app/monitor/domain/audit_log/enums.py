from enum import Enum


class AuditResultEnum(str, Enum):
    """审计结果（成功 / 失败）。

    失败原因用 `error_code`（机读）与 `error_message`（人读）表达，不在此展开枚举。
    """
    SUCCESS = 'success'
    FAILURE = 'failure'
