import type { ApiErrorBody } from './types'

/**
 * 归一后的 API 错误——对应后端业务异常的 `code` / `message` / `details`。
 * 调用方按 `code` 区分（与后端「code 当稳定接口」的约定一致）。
 */
export class ApiError extends Error {
  readonly code: string
  readonly status?: number
  readonly details?: unknown

  constructor(body: ApiErrorBody, status?: number) {
    super(body.message)
    this.name = 'ApiError'
    this.code = body.code
    this.details = body.details
    this.status = status
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}
