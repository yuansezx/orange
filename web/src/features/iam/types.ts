/** iam 资源共用的状态（对齐后端 `StatusEnum`）。 */
export type Status = 'active' | 'disabled'

/** 数据范围（对齐后端 `DataScopeEnum`）。 */
export type DataScope = 'all' | 'dept' | 'dept_and_child' | 'custom' | 'self'

/** 审计信息（平铺，对齐后端 `AuditOut`）——时间 + 人（用户名/昵称）。 */
export interface AuditFields {
  created_at: string
  created_by_username: string | null
  created_by_nickname: string | null
  updated_at: string | null
  updated_by_username: string | null
  updated_by_nickname: string | null
  deleted_at: string | null
  deleted_by_username: string | null
  deleted_by_nickname: string | null
}

/** 部门引用（对齐后端 `DeptRefOut`）：id + 名称 + 层级路径（根→自身）。 */
export interface DeptRef {
  id: string
  name: string
  path: string
}
