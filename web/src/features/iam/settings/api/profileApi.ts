import { del, get, put } from '@shared/api'

import type { MyProfile, UpdateMyProfileReq } from '../types'

const BASE = '/api/iam/users/me/profile'
const AVATAR = '/api/iam/users/me/avatar'

export function getMyProfile(): Promise<MyProfile> {
  return get<MyProfile>(BASE)
}

/** PUT 完整替换：email / phone 传 null 表示清除绑定。 */
export function updateMyProfile(body: UpdateMyProfileReq): Promise<MyProfile> {
  return put<MyProfile>(BASE, body)
}

export function uploadMyAvatar(file: File): Promise<MyProfile> {
  const form = new FormData()
  form.append('file', file)
  return put<MyProfile>(AVATAR, form)
}

export function deleteMyAvatar(): Promise<void> {
  return del<void>(AVATAR)
}
