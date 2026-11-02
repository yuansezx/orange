import { del, get } from '@shared/api'

import type { MySession } from '../types'

const BASE = '/api/iam/users/me/sessions'

export function getMySessions(): Promise<MySession[]> {
  return get<MySession[]>(BASE)
}

/** 退出本人指定会话（当前会话也可传，等同退出登录）。 */
export function revokeMySessions(sessionIds: string[]): Promise<void> {
  return del<void>(BASE, { data: { session_ids: sessionIds } })
}
