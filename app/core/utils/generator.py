"""各类随机/唯一值的生成（纯计算，无业务语义）。"""
import secrets

# 临时密码字符集：去掉易混淆字符（0/O、1/l/I）
_PASSWORD_ALPHABET = (
    'abcdefghijkmnpqrstuvwxyz'
    'ABCDEFGHJKLMNPQRSTUVWXYZ'
    '23456789'
)
DEFAULT_PASSWORD_LENGTH = 16


def generate_password(length: int = DEFAULT_PASSWORD_LENGTH) -> str:
    return ''.join(secrets.choice(_PASSWORD_ALPHABET) for _ in range(length))
