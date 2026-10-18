import { del, get, post, put } from '@shared/api'
import type { PageResult } from '@shared/api'

import type {
  CreateUserReq,
  GetUsersQuery,
  UpdateUserReq,
  UserDetail,
  UserListItem,
  UserStatus,
} from '../types'

const BASE = '/api/iam/users'

export async function getUsers(query: GetUsersQuery): Promise<PageResult<UserListItem>> {
  const page = await get<PageResult<UserListItem>>(BASE, query)
  return { ...page, data: page.data ?? [] }
}

/** 用户详情（含审计 / 部门引用 / 角色）——回收站内亦可读。 */
export function getUserDetail(id: string): Promise<UserDetail> {
  return get<UserDetail>(`${BASE}/${id}/detail`)
}

export function createUser(body: CreateUserReq): Promise<void> {
  return post<void>(BASE, body)
}

export function updateUser(id: string, body: UpdateUserReq): Promise<void> {
  return put<void>(`${BASE}/${id}`, body)
}

export function deleteUser(id: string): Promise<void> {
  return del<void>(`${BASE}/${id}`)
}

/** 启用 / 停用（统一状态接口）。 */
export function setUserStatus(id: string, status: UserStatus): Promise<void> {
  return put<void>(`${BASE}/${id}/status`, { status })
}
