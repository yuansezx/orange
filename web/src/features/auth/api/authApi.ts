import { get, post } from '@shared/api'

import type { CurrentUser, LoginReq, LoginResp } from '../types'

/** 认证三件套（对齐后端 `iam/interface/http/auth/api.py`）。 */
export function login(body: LoginReq): Promise<LoginResp> {
  return post<LoginResp>('/iam/auth/login', body)
}

export function logout(): Promise<void> {
  return post<void>('/iam/auth/logout')
}

export function getMe(): Promise<CurrentUser> {
  return get<CurrentUser>('/iam/auth/me')
}
