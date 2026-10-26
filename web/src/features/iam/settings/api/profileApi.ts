import { get, put } from '@shared/api'

import type { MyProfile, UpdateMyProfileReq } from '../types'

const BASE = '/api/iam/users/me/profile'

export function getMyProfile(): Promise<MyProfile> {
  return get<MyProfile>(BASE)
}

/** PUT 完整替换：email / phone 传 null 表示清除绑定。 */
export function updateMyProfile(body: UpdateMyProfileReq): Promise<MyProfile> {
  return put<MyProfile>(BASE, body)
}
