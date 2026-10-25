import { del, get } from '@shared/api'

import type { SessionItem } from '../types'

const BASE = '/api/iam/sessions'

export function getSessions(): Promise<SessionItem[]> {
  return get<SessionItem[]>(BASE)
}

/** 踢出该用户的指定会话（可跨多个用户，按用户分别调用）。 */
export function revokeUserSessions(userId: string, sessionIds: string[]): Promise<void> {
  return del<void>(`${BASE}/${userId}`, { data: { session_ids: sessionIds } })
}

/** 踢出多个用户的全部会话。 */
export function revokeUsers(userIds: string[]): Promise<void> {
  return del<void>(BASE, { data: { user_ids: userIds } })
}
