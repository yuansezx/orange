from datetime import datetime, UTC

import future_uuid as uuid

from app.core.domain.value_objects import BaseEntityId
from app.iam.domain.dept.ports import DeptIdProvider
from app.iam.domain.role.ports import RoleIdProvider
from app.iam.domain.user.ports import UserIdProvider
from app.iam.domain.shared.value_objects import RoleId, DeptId, UserId, UserRoleId
from app.iam.domain.user_role_assignment.ports import UserRoleIdProvider


def _extract_uuid7_datetime(entity_id: BaseEntityId) -> datetime:
    uuid_obj = uuid.UUID(entity_id.value)
    timestamp_ms = uuid_obj.int >> 80
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class UserIdProviderUUID7Impl(UserIdProvider):
    def generate(self) -> UserId:
        return UserId(value=str(uuid.uuid7()))

    def extract_datetime(self, entity_id: UserId) -> datetime:
        return _extract_uuid7_datetime(entity_id)


class RoleIdProviderUUID7Impl(RoleIdProvider):
    def generate(self) -> RoleId:
        return RoleId(value=str(uuid.uuid7()))

    def extract_datetime(self, entity_id: RoleId) -> datetime:
        return _extract_uuid7_datetime(entity_id)


class DeptIdProviderUUID7Impl(DeptIdProvider):
    def generate(self) -> DeptId:
        return DeptId(value=str(uuid.uuid7()))

    def extract_datetime(self, entity_id: DeptId) -> datetime:
        return _extract_uuid7_datetime(entity_id)


class UserRoleIdProviderUUID7Impl(UserRoleIdProvider):
    def generate(self) -> UserRoleId:
        return UserRoleId(value=str(uuid.uuid7()))

    def extract_datetime(self, entity_id: UserRoleId) -> datetime:
        return _extract_uuid7_datetime(entity_id)
