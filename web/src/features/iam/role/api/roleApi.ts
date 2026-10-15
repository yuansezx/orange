import { del, get, post, put } from '@shared/api'

import type { Catalog, CreateRoleReq, Role, RoleDetail, UpdateRoleReq } from '../types'

const BASE = '/iam/roles'

export function getRoles(): Promise<Role[]> {
  return get<Role[]>(BASE)
}

export function getRole(id: string): Promise<RoleDetail> {
  return get<RoleDetail>(`${BASE}/${id}`)
}

export function createRole(body: CreateRoleReq): Promise<RoleDetail> {
  return post<RoleDetail>(BASE, body)
}

export function updateRole(id: string, body: UpdateRoleReq): Promise<void> {
  return put<void>(`${BASE}/${id}`, body)
}

export function deleteRole(id: string): Promise<void> {
  return del<void>(`${BASE}/${id}`)
}

/** 资源/权限目录（角色页权限树用）——`GET /iam/resources/catalog`。 */
export function getPermissionCatalog(): Promise<Catalog> {
  return get<Catalog>('/iam/resources/catalog')
}
