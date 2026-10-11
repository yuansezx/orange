import { get } from '@shared/api'
import type { PageResult } from '@shared/api'

import type { GetUsersQuery, UserListItem } from '../types'

const BASE = '/iam/users'

export async function getUsers(query: GetUsersQuery): Promise<PageResult<UserListItem>> {
  const page = await get<PageResult<UserListItem>>(BASE, query)
  return { ...page, data: page.data ?? [] }
}
