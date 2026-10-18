import { get } from '@shared/api'
import type { PageResult } from '@shared/api'

import type { GetUsersQuery, UserDetail, UserListItem } from '../types'

const BASE = '/api/iam/users'

export async function getUsers(query: GetUsersQuery): Promise<PageResult<UserListItem>> {
  const page = await get<PageResult<UserListItem>>(BASE, query)
  return { ...page, data: page.data ?? [] }
}

/** 用户详情（含审计 / 部门引用 / 角色）——回收站内亦可读。 */
export function getUserDetail(id: string): Promise<UserDetail> {
  return get<UserDetail>(`${BASE}/${id}/detail`)
}
