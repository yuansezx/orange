from enum import Enum


class AuditResultEnum(str, Enum):
    """审计结果（成功 / 失败）。

    失败原因用 `error_code`（机读）与 `error_message`（人读）表达，不在此展开枚举。
    """
    SUCCESS = 'success'
    FAILURE = 'failure'


class AuthMethodEnum(str, Enum):
    """单次认证来源（审计用）。

    登录事件记 password / oauth；业务动作记 session / api_key。
    会话最初如何登录（password/oauth）属于会话元数据，不在每条动作审计里重复。
    """
    PASSWORD = 'password'
    SESSION = 'session'
    API_KEY = 'api_key'
    OAUTH = 'oauth'
