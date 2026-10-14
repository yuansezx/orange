import type { Status } from '../types'

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

/** 部门树节点——对齐后端 `DeptTreeNodeResp`（`children` 递归）。 */
export interface DeptTreeNode extends Dept {
  children: DeptTreeNode[]
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
