/** iam 资源共用的状态（对齐后端 `StatusEnum`）。 */
export type Status = 'active' | 'disabled'

/** 数据范围（对齐后端 `DataScopeEnum`）。 */
export type DataScope = 'all' | 'dept' | 'dept_and_child' | 'custom' | 'self'

/** 审计操作人（对齐后端 `OperatorOut`）；用户被硬删后名字为 null。 */
export interface OperatorRef {
  id: string
  username: string | null
  nickname: string | null
}

/** 审计块：生命周期时间（数据 DTO）+ 操作人（后端 `AuditOut`）。 */
export interface AuditFields {
  created_at: string
  updated_at: string | null
  deleted_at: string | null
  created_by: OperatorRef | null
  updated_by: OperatorRef | null
  deleted_by: OperatorRef | null
}

/** 部门引用（对齐后端 `DeptRefOut`）：id + 名称 + 层级路径（根→自身）。 */
export interface DeptRef {
  id: string
  name: string
  path: string
}
