from app.core.domain.ports import IdProviderPort
from app.iam.domain.shared.value_objects import UserRoleId


class UserRoleIdProviderPort(IdProviderPort[UserRoleId]):
    pass