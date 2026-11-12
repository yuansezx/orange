import hashlib
import hmac


def hash_secret(secret: str) -> str:
    """高熵随机凭据的摘要（SHA-256 hex）。

    适用于 API Key、OAuth client secret 这类**随机生成**的凭据：熵足够高，
    不需要 bcrypt 之类的慢哈希；数据库只存摘要，明文只在创建时展示一次。
    """
    return hashlib.sha256(secret.encode('utf-8')).hexdigest()


def verify_secret(secret: str, secret_hash: str) -> bool:
    """恒定时间比较，避免时序侧信道。"""
    return hmac.compare_digest(hash_secret(secret), secret_hash)
