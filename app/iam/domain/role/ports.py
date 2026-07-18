from app.core.domain.ports import IdProvider
from app.iam.domain.shared.value_objects import RoleId


class RoleIdProvider(IdProvider[RoleId]):
    pass