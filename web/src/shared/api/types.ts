/** 后端统一错误体（见 app/interface/http/exception_handlers.py）。 */
export interface ApiErrorBody {
  code: string
  message: string
  details?: unknown
}

/** 后端分页结果（对应 core/utils/schemas.py 的 PageResult）。 */
export interface PageResult<T> {
  page: number
  page_size: number
  total: number
  total_pages: number
  data: T[] | null
}

/** 分页查询入参基元，各资源按需扩展。 */
export interface PageQuery {
  page?: number
  page_size?: number
}
