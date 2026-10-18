import { del, get, post, put } from '@shared/api'

import type { CreateDeptReq, Dept, DeptDetail, DeptTreeNode, UpdateDeptReq } from '../types'

const BASE = '/api/iam/depts'

/** 部门树（嵌套）——列表页主数据。 */
export function getDeptTree(): Promise<DeptTreeNode[]> {
  return get<DeptTreeNode[]>(`${BASE}/tree`)
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
