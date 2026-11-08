import { del, get, patch, post, put } from '@shared/api'
import type { PageResult } from '@shared/api'

import type { Status } from '../../types'
import type {
  Catalog,
  CreateRoleReq,
  GetRoleCandidatesQuery,
  GetRoleMembersQuery,
  PatchRoleUsersReq,
  Role,
  RoleCandidateUser,
  RoleDetail,
  RoleListItem,
  RoleMember,
  UpdateRoleReq,
} from '../types'

const BASE = '/api/iam/roles'

export function getRoles(deleted = false): Promise<RoleListItem[]> {
  return get<RoleListItem[]>(BASE, deleted ? { deleted: true } : undefined)
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

/** 角色成员（分页只读；含自助停用的分配）。 */
export function getRoleMembers(
  id: string,
  query: GetRoleMembersQuery,
): Promise<PageResult<RoleMember>> {
  return get<PageResult<RoleMember>>(`${BASE}/${id}/users`, query)
}

/** 角色成员候选：分页 + 每行 selected 标记（数据范围/关键词由后端处理）。 */
export function getRoleCandidates(
  id: string,
  query: GetRoleCandidatesQuery,
): Promise<PageResult<RoleCandidateUser>> {
  return get<PageResult<RoleCandidateUser>>(`${BASE}/${id}/candidates`, query)
}

/** 角色成员管理（增量）：只提交本次增删的用户。 */
export function patchRoleUsers(id: string, body: PatchRoleUsersReq): Promise<void> {
  return patch<void>(`${BASE}/${id}/users`, body)
}

export function deleteRole(id: string): Promise<void> {
  return del<void>(`${BASE}/${id}`)
}

/** 启用 / 停用（统一状态接口）。 */
export function setRoleStatus(id: string, status: Status): Promise<void> {
  return put<void>(`${BASE}/${id}/status`, { status })
}

/** 回收站：恢复（复用删除权限）。 */
export function restoreRole(id: string): Promise<void> {
  return post<void>(`${BASE}/${id}/restore`)
}

/** 回收站：彻底删除（物理，不可恢复）。 */
export function hardDeleteRole(id: string): Promise<void> {
  return del<void>(`${BASE}/${id}/hard-delete`)
}

/** 资源/权限目录（角色页权限树用）——`GET /api/iam/resources/catalog`。 */
export function getPermissionCatalog(): Promise<Catalog> {
  return get<Catalog>('/api/iam/resources/catalog')
}
