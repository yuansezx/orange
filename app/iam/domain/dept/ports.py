from app.core.domain.ports import IdProvider
from app.iam.domain.shared.value_objects import DeptId


class DeptIdProvider(IdProvider[DeptId]):
    pass