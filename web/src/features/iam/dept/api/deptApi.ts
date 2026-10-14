import { del, get, post, put } from '@shared/api'

import type { CreateDeptReq, Dept, DeptTreeNode, UpdateDeptReq } from '../types'

const BASE = '/iam/depts'

/** 部门树（嵌套）——列表页主数据。 */
export function getDeptTree(): Promise<DeptTreeNode[]> {
  return get<DeptTreeNode[]>(`${BASE}/tree`)
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
