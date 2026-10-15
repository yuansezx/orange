/** iam 资源共用的状态（对齐后端 `StatusEnum`）。 */
export type Status = 'active' | 'disabled' | 'deleted'

/** 数据范围（对齐后端 `DataScopeEnum`）。 */
export type DataScope = 'all' | 'dept' | 'dept_and_child' | 'custom' | 'self'
