import { get, post } from '@shared/api'

import type { CurrentUser, LoginReq, LoginResp } from '../types'

/** 登录 / 登出（对齐后端 `auth/api.py`）；当前用户走 users 资源。 */
export function login(body: LoginReq): Promise<LoginResp> {
  return post<LoginResp>('/api/iam/auth/login', body)
}

export function logout(): Promise<void> {
  return post<void>('/api/iam/auth/logout')
}

export function getMe(): Promise<CurrentUser> {
  return get<CurrentUser>('/api/iam/users/me')
}
