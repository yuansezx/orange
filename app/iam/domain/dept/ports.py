from app.core.domain.ports import IdProviderPort
from app.iam.domain.shared.value_objects import DeptId


class DeptIdProviderPort(IdProviderPort[DeptId]):
    pass