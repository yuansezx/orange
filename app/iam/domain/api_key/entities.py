from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime, UTC

from pydantic import field_validator, model_validator

from app.core.domain.entities import AuditableEntity
from app.core.utils.secret_hash import verify_secret
from app.iam.domain.api_key.exceptions import (
    InvalidApiKeyDataScopeException,
    InvalidApiKeyExpiryException,
    InvalidApiKeyNameException,
    InvalidApiKeyScopeException,
    InvalidApiKeyTokenException,
)
from app.iam.domain.shared.enums import DataScopeEnum, StatusEnum
from app.iam.domain.shared.value_objects import ApiKeyId, DeptId, UserId

API_KEY_NAME_MAX_LENGTH = 64
TOKEN_MASKED_MAX_LENGTH = 32
TOKEN_HASH_PATTERN = re.compile(r'^[0-9a-f]{64}$')
PERMISSION_CODE_PATTERN = re.compile(r'^[^:\s]+:[^:\s]+:[^:\s]+$')
# DEPT / DEPT_AND_CHILD 是角色数据范围的语义，key 只接收已解析的部门集合（CUSTOM）。
KEY_DATA_SCOPE_KINDS = frozenset({DataScopeEnum.ALL, DataScopeEnum.SELF, DataScopeEnum.CUSTOM})


class ApiKey(AuditableEntity[UserId]):
    """用户 API Key（PAT）：用户的第二凭据，**不是独立主体**。

    - `user_id` 是凭据所属用户；认证后仍以该用户身份行事。
    - `scopes` 是用户在自有权限内勾选的子集；生效权限 = 用户当前权限 ∩ scopes。
    - `data_scope_*` 是数据范围限制；生效范围 = 用户数据范围与此限制取更严格者。
    - `token_hash` 存整串 token 的 SHA-256，明文只在创建时展示一次；`token_masked` 只是展示用掩码，不是明文、不可认证。
    - `status` 只表启停；`deleted_at` 表吊销（软删）。**不提供恢复**——已吊销的凭据不应复活。
    - `last_used_at` 是使用痕迹（节流写），不属于管理变更，不盖 `updated_at/updated_by`。
    """

    id: ApiKeyId                                      # 实体标识（管理 / 审计 / 缓存引用）
    user_id: UserId                                   # 凭据所属用户；认证后以该用户身份行事
    name: str                                         # 用户可见名称，用于区分多把 key
    token_hash: str                                   # 整串 token 的 SHA-256；明文只在创建时展示一次
    token_masked: str                                 # 展示用掩码（如 orange_ak_••••a1b2）；非明文、不可认证，明文不落库
    scopes: frozenset[str]                            # 勾选的权限码子集；生效权限 = 用户当前权限 ∩ scopes
    data_scope_kind: DataScopeEnum                    # 数据范围限制：ALL＝不限制 / SELF / CUSTOM
    status: StatusEnum                                # 启停（ACTIVE/DISABLED）；与吊销 deleted_at 正交
    data_scope_dept_ids: frozenset[DeptId] = frozenset()  # 仅 CUSTOM 使用：允许访问的部门集合
    expires_at: datetime | None = None                # 过期时间（带时区）；None＝不限期
    last_used_at: datetime | None = None              # 最近使用时间（节流写）；None＝从未使用

    @staticmethod
    def _normalize_name(value: str) -> str:
        value = value.strip()
        if not value or len(value) > API_KEY_NAME_MAX_LENGTH:
            raise InvalidApiKeyNameException(
                f'API Key 名称长度必须在 1-{API_KEY_NAME_MAX_LENGTH} 之间')
        return value

    @field_validator('name')
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return cls._normalize_name(value)

    @field_validator('token_hash')
    @classmethod
    def _validate_token_hash(cls, value: str) -> str:
        if not TOKEN_HASH_PATTERN.fullmatch(value):
            raise InvalidApiKeyTokenException('token_hash 必须是 SHA-256 十六进制摘要')
        return value

    @field_validator('token_masked')
    @classmethod
    def _validate_token_masked(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > TOKEN_MASKED_MAX_LENGTH:
            raise InvalidApiKeyTokenException(
                f'令牌掩码长度必须在 1-{TOKEN_MASKED_MAX_LENGTH} 之间')
        return value

    @classmethod
    def _normalize_scopes(cls, scopes: Iterable[str]) -> frozenset[str]:
        if isinstance(scopes, str):
            raise InvalidApiKeyScopeException('权限子集必须是权限码集合，不能是单个字符串')
        normalized = frozenset(code.strip() for code in scopes)
        if not normalized:
            raise InvalidApiKeyScopeException('API Key 至少需要选择一个权限')
        for code in normalized:
            if not PERMISSION_CODE_PATTERN.fullmatch(code):
                raise InvalidApiKeyScopeException(f'权限码格式非法：{code!r}')
        return normalized

    @field_validator('scopes')
    @classmethod
    def _validate_scopes(cls, value: frozenset[str]) -> frozenset[str]:
        return cls._normalize_scopes(value)

    @classmethod
    def _normalize_data_scope(cls, kind: DataScopeEnum,
                              dept_ids: Iterable[DeptId]) -> tuple[DataScopeEnum, frozenset[DeptId]]:
        dept_ids = frozenset(DeptId(d) for d in dept_ids)
        if kind not in KEY_DATA_SCOPE_KINDS:
            raise InvalidApiKeyDataScopeException(
                f'API Key 数据范围只支持 ALL / SELF / CUSTOM，收到：{kind.value}')
        if kind is DataScopeEnum.CUSTOM:
            if not dept_ids:
                raise InvalidApiKeyDataScopeException('CUSTOM 数据范围必须指定部门')
        elif dept_ids:
            raise InvalidApiKeyDataScopeException('非 CUSTOM 数据范围不能指定部门')
        return kind, dept_ids

    @model_validator(mode='after')
    def _check_data_scope(self):
        self._normalize_data_scope(self.data_scope_kind, self.data_scope_dept_ids)
        return self

    @field_validator('expires_at')
    @classmethod
    def _validate_expires_at(cls, value: datetime | None) -> datetime | None:
        return cls._normalize_expires_at(value)

    @staticmethod
    def _normalize_expires_at(value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise InvalidApiKeyExpiryException('expires_at 必须带时区')
        return value

    # ---------------- 认证 ----------------

    def verify_token(self, token: str) -> bool:
        """恒定时间校验整串 token（含前缀）。"""
        return verify_secret(token, self.token_hash)

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at is not None and self.expires_at <= now

    def can_authenticate(self, now: datetime) -> bool:
        """是否可作为凭据使用：未吊销、已启用、未过期。所属用户的状态由应用层判定。"""
        return (not self.is_deleted
                and self.status is StatusEnum.ACTIVE
                and not self.is_expired(now))

    # ---------------- 管理变更 ----------------

    def rename(self, name: str, operator_id: UserId) -> None:
        self.name = self._normalize_name(name)
        self._stamp(operator_id)

    def change_scopes(self, scopes: Iterable[str], operator_id: UserId) -> None:
        self.scopes = self._normalize_scopes(scopes)
        self._stamp(operator_id)

    def change_data_scope(self, kind: DataScopeEnum, dept_ids: Iterable[DeptId],
                          operator_id: UserId) -> None:
        self.data_scope_kind, self.data_scope_dept_ids = self._normalize_data_scope(kind, dept_ids)
        self._stamp(operator_id)

    def change_expiry(self, expires_at: datetime | None, operator_id: UserId) -> None:
        self.expires_at = self._normalize_expires_at(expires_at)
        self._stamp(operator_id)

    def change_status(self, status: StatusEnum, operator_id: UserId) -> None:
        self.status = status
        self._stamp(operator_id)

    def mark_used(self, used_at: datetime) -> None:
        """记录最近使用时间（节流写）；不属于管理变更，不盖 updated 审计。"""
        self.last_used_at = used_at

    def delete(self, operator_id: UserId) -> None:
        """吊销：软删除，只写 deleted_at/by，不动 status（停用状态得以保留）。"""
        self.deleted_by = operator_id
        self.deleted_at = datetime.now(UTC)
        self._stamp(operator_id)

    def _stamp(self, operator_id: UserId) -> None:
        self.updated_by = operator_id
        self.updated_at = datetime.now(UTC)
