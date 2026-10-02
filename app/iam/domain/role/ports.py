from app.core.domain.ports import IdProviderPort
from app.iam.domain.shared.value_objects import RoleId


class RoleIdProviderPort(IdProviderPort[RoleId]):
    pass