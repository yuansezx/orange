"""共享的数据范围解析服务——**与实体无关**。

同一个人，看「用户列表」和「角色列表」，范围是同一套 roles/depts 算出来的，
所以解析收在这里，各实体的应用服务共用；实体的**应用**（能否动某条）各自做。
"""
from app.iam.domain.current_user.entities import CurrentUser
from app.iam.domain.shared.value_objects import DataScopeSpec
from app.iam.domain.user.enums import UserTypeEnum


class DataScopeService:

    async def data_scope_of(self, current_user: CurrentUser) -> DataScopeSpec:
        """解析用户的有效数据范围。超管 → ALL。

        其余需读 user_role → 角色 data_scope + custom_dept_ids 合并；DEPT_AND_CHILD 需部门树。
        """
        if current_user.user_type == UserTypeEnum.SUPER_ADMIN:
            return DataScopeSpec.all()
        # TODO: 非超管——读 user_role / role 合并范围；DEPT_AND_CHILD 依赖部门树
        raise NotImplementedError('非超管的数据范围解析待实现（角色 data_scope + 部门树）')
