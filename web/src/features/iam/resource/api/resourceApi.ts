import { del, get, post, put } from '@shared/api'

import type { Status } from '../../types'
import type {
  CreatePermissionReq,
  CreateResourceReq,
  GetResourcesQuery,
  PermissionListItem,
  Resource,
  UpdatePermissionReq,
  UpdateResourceReq,
} from '../types'

const RESOURCES = '/api/iam/resources'
const PERMISSIONS = '/api/iam/permissions'

export function getResources(query: GetResourcesQuery = {}): Promise<Resource[]> {
  return get<Resource[]>(RESOURCES, query)
}

/** 扁平权限列表；`deleted=true` = 权限回收站。 */
export function getPermissions(deleted = false): Promise<PermissionListItem[]> {
  return get<PermissionListItem[]>(PERMISSIONS, { deleted })
}

export function createResource(body: CreateResourceReq): Promise<Resource> {
  return post<Resource>(RESOURCES, body)
}

export function updateResource(id: string, body: UpdateResourceReq): Promise<void> {
  return put<void>(`${RESOURCES}/${id}`, body)
}

export function setResourceStatus(id: string, status: Status): Promise<void> {
  return put<void>(`${RESOURCES}/${id}/status`, { status })
}

export function deleteResource(id: string): Promise<void> {
  return del<void>(`${RESOURCES}/${id}`)
}

export function restoreResource(id: string): Promise<void> {
  return post<void>(`${RESOURCES}/${id}/restore`)
}

export function hardDeleteResource(id: string): Promise<void> {
  return del<void>(`${RESOURCES}/${id}/hard-delete`)
}

export function createPermission(body: CreatePermissionReq): Promise<void> {
  return post<void>(PERMISSIONS, body)
}

export function updatePermission(id: string, body: UpdatePermissionReq): Promise<void> {
  return put<void>(`${PERMISSIONS}/${id}`, body)
}

export function setPermissionStatus(id: string, status: Status): Promise<void> {
  return put<void>(`${PERMISSIONS}/${id}/status`, { status })
}

export function deletePermission(id: string): Promise<void> {
  return del<void>(`${PERMISSIONS}/${id}`)
}

export function restorePermission(id: string): Promise<void> {
  return post<void>(`${PERMISSIONS}/${id}/restore`)
}

export function hardDeletePermission(id: string): Promise<void> {
  return del<void>(`${PERMISSIONS}/${id}/hard-delete`)
}
