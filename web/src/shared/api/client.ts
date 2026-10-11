import axios from 'axios'
import type { AxiosError, AxiosRequestConfig } from 'axios'

import { getToken } from '@shared/auth/token'

import { ApiError } from './errors'
import type { ApiErrorBody } from './types'

/**
 * 唯一 HTTP 客户端（六边形里的「适配器」）：注入令牌 + 归一后端错误体。
 * baseURL 为 `/`，dev 下经 vite proxy 转发到 FastAPI（模块前缀 /iam）。
 */
export const http = axios.create({
  baseURL: '/',
  timeout: 15_000,
})

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (res) => res,
  (error: AxiosError<ApiErrorBody>) => {
    const body = error.response?.data
    if (body && typeof body === 'object' && 'code' in body) {
      return Promise.reject(new ApiError(body, error.response?.status))
    }
    return Promise.reject(
      new ApiError({ code: 'NETWORK_ERROR', message: error.message }, error.response?.status),
    )
  },
)

export async function get<T>(url: string, params?: object, config?: AxiosRequestConfig): Promise<T> {
  const res = await http.get<T>(url, { params, ...config })
  return res.data
}

export async function post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const res = await http.post<T>(url, data, config)
  return res.data
}

export async function put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const res = await http.put<T>(url, data, config)
  return res.data
}

export async function del<T = void>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const res = await http.delete<T>(url, config)
  return res.data
}
