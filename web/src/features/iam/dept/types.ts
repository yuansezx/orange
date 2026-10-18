import type { AuditFields, DeptRef, Status } from '../types'

/** 部门读模型——字段对齐后端 `DeptResp`。 */
export interface Dept {
  id: string
  name: string
  parent_id: string | null
  leader_id: string | null
  email: string | null
  phone: string | null
  status: Status
  description: string | null
  created_at: string
}

/** 部门详情——对齐后端 `DeptDetailResp`（数据 + 审计 + 上级部门引用 + 负责人）。 */
export interface DeptDetail extends Dept, AuditFields {
  parent: DeptRef | null
  leader_username: string | null
  leader_nickname: string | null
}

/** 部门树节点——对齐后端 `DeptTreeNodeResp`（`children` 递归）。 */
export interface DeptTreeNode extends Dept {
  children: DeptTreeNode[]
}

/** 部门扁平列表项（回收站）——对齐后端 `DeptListItemResp`（数据 + 审计）。 */
export interface DeptListItem extends Dept, AuditFields {}

/** 扁平列表查询参数。 */
export interface GetDeptsQuery {
  name?: string
  status?: Status
  deleted?: boolean
}

/** 创建部门——对齐后端 `CreateDeptReq`（无 `status`，服务端默认 ACTIVE）。 */
export interface CreateDeptReq {
  name: string
  parent_id?: string | null
  leader_id?: string | null
  email?: string | null
  phone?: string | null
  description?: string | null
}

/** 更新部门——对齐后端 `UpdateDeptReq`；**移动 = 带新 `parent_id`**。 */
export interface UpdateDeptReq {
  name?: string
  parent_id?: string | null
  leader_id?: string | null
  email?: string | null
  phone?: string | null
  description?: string | null
  status?: Status
}

/** 表单值（父部门/负责人用 id 或空）。 */
export interface DeptFormValues {
  name: string
  parent_id?: string
  leader_id?: string
  email?: string
  phone?: string
  description?: string
  status?: Status
}
