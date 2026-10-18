import { del, get, post, put } from '@shared/api'

import type {
  Catalog,
  CreateRoleReq,
  Role,
  RoleDetail,
  RoleListItem,
  UpdateRoleReq,
} from '../types'

const BASE = '/api/iam/roles'

export function getRoles(): Promise<RoleListItem[]> {
  return get<RoleListItem[]>(BASE)
}

export function getRole(id: string): Promise<Role> {
  return get<Role>(`${BASE}/${id}`)
}

/** 角色详情（含审计 / 部门引用）。 */
export function getRoleDetail(id: string): Promise<RoleDetail> {
  return get<RoleDetail>(`${BASE}/${id}/detail`)
}

export function createRole(body: CreateRoleReq): Promise<Role> {
  return post<Role>(BASE, body)
}

export function updateRole(id: string, body: UpdateRoleReq): Promise<void> {
  return put<void>(`${BASE}/${id}`, body)
}

export function deleteRole(id: string): Promise<void> {
  return del<void>(`${BASE}/${id}`)
}

/** 资源/权限目录（角色页权限树用）——`GET /api/iam/resources/catalog`。 */
export function getPermissionCatalog(): Promise<Catalog> {
  return get<Catalog>('/api/iam/resources/catalog')
}
