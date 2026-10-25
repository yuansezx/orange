import { get, post, put } from '@shared/api'

import type { ChangePasswordReq, CurrentUser, LoginReq, LoginResp } from '../types'

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

/** 自助改密（成功后服务端吊销全部会话，需重新登录）。 */
export function changePassword(body: ChangePasswordReq): Promise<void> {
  return put<void>('/api/iam/users/me/password', body)
}
