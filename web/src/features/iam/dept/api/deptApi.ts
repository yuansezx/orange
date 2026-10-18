import { del, get, post, put } from '@shared/api'

import type { Status } from '../../types'
import type {
  CreateDeptReq,
  Dept,
  DeptDetail,
  DeptListItem,
  DeptTreeNode,
  GetDeptsQuery,
  UpdateDeptReq,
} from '../types'

const BASE = '/api/iam/depts'

/** 部门树（嵌套）——列表页主数据。 */
export function getDeptTree(): Promise<DeptTreeNode[]> {
  return get<DeptTreeNode[]>(`${BASE}/tree`)
}

/** 扁平列表（含审计）——回收站视图。 */
export function getDepts(query: GetDeptsQuery): Promise<DeptListItem[]> {
  return get<DeptListItem[]>(BASE, query)
}

/** 部门详情（含审计 / 上级部门引用 / 负责人）。 */
export function getDeptDetail(id: string): Promise<DeptDetail> {
  return get<DeptDetail>(`${BASE}/${id}/detail`)
}

export function createDept(body: CreateDeptReq): Promise<Dept> {
  return post<Dept>(BASE, body)
}

export function updateDept(id: string, body: UpdateDeptReq): Promise<Dept> {
  return put<Dept>(`${BASE}/${id}`, body)
}

export function deleteDept(id: string): Promise<void> {
  return del<void>(`${BASE}/${id}`)
}

/** 启用 / 停用（统一状态接口；停用级联子树、启用级联祖先）。 */
export function setDeptStatus(id: string, status: Status): Promise<void> {
  return put<void>(`${BASE}/${id}/status`, { status })
}

/** 回收站：恢复（复用删除权限；祖先非全启用时恢复为停用）。 */
export function restoreDept(id: string): Promise<void> {
  return post<void>(`${BASE}/${id}/restore`)
}

/** 回收站：彻底删除（物理，级联整棵已删子树）。 */
export function hardDeleteDept(id: string): Promise<void> {
  return del<void>(`${BASE}/${id}/hard-delete`)
}
