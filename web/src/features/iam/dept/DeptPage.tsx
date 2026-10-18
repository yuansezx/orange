import { App } from 'antd'
import { useMemo, useState } from 'react'

import { Platform } from '@shared/platform'

import { DeptDetailDrawer } from './components/DeptDetailDrawer'
import { DeptFormDialog } from './components/DeptFormDialog'
import { DeptToolbar } from './components/DeptToolbar'
import { DeptTable } from './components/desktop/DeptTable'
import { DeptTreeList } from './components/mobile/DeptTreeList'
import { useDeptMutations } from './hooks/useDeptMutations'
import { useDeptTree } from './hooks/useDeptTree'
import type { Dept, DeptFormValues, DeptTreeNode } from './types'

/** 关键字过滤：保留命中节点及其祖先链（子树命中则保留父）。 */
function filterTree(nodes: DeptTreeNode[], keyword: string): DeptTreeNode[] {
  const query = keyword.trim().toLowerCase()
  if (!query) return nodes
  const result: DeptTreeNode[] = []
  for (const node of nodes) {
    const children = filterTree(node.children ?? [], keyword)
    if (node.name.toLowerCase().includes(query) || children.length > 0) {
      result.push({ ...node, children })
    }
  }
  return result
}

function collectSubtreeIds(node: DeptTreeNode): string[] {
  return [node.id, ...(node.children ?? []).flatMap(collectSubtreeIds)]
}

function findNode(nodes: DeptTreeNode[], id: string): DeptTreeNode | undefined {
  for (const node of nodes) {
    if (node.id === id) return node
    const hit = findNode(node.children ?? [], id)
    if (hit) return hit
  }
  return undefined
}

interface DialogState {
  open: boolean
  mode: 'create' | 'edit' | 'view'
  dept?: Dept
  parentId?: string
}

/**
 * 部门管理页：树表格 + 增删改 + 移动 + 查看详情（点行进入只读）。
 * 取数（useDeptTree）与表单两端共用；仅列表渲染按设备分叉（<Platform>）。
 * 移动 = 编辑时改「上级部门」；删除守卫由后端判定，错误经 message 展示。
 */
export default function DeptPage() {
  const { data: tree = [], isLoading, error } = useDeptTree()
  const { create, update, remove, setStatus } = useDeptMutations()
  const { modal } = App.useApp()
  const [keyword, setKeyword] = useState('')
  const [dialog, setDialog] = useState<DialogState>({ open: false, mode: 'create' })

  const nodes = useMemo(() => filterTree(tree, keyword), [tree, keyword])

  // 编辑时把自身及子孙从「上级部门」候选里禁用（防环）
  const excludeIds = useMemo(() => {
    if (dialog.mode !== 'edit' || !dialog.dept) return undefined
    const node = findNode(tree, dialog.dept.id)
    return node ? collectSubtreeIds(node) : [dialog.dept.id]
  }, [dialog, tree])

  const openCreate = (parentId?: string) => setDialog({ open: true, mode: 'create', parentId })
  const openView = (dept: Dept) => setDialog({ open: true, mode: 'view', dept })
  const openEdit = (dept: Dept) => setDialog({ open: true, mode: 'edit', dept })
  const close = () => setDialog((prev) => ({ ...prev, open: false }))

  const toBody = (values: DeptFormValues) => ({
    name: values.name.trim(),
    parent_id: values.parent_id ?? null,
    leader_id: values.leader_id ?? null,
    email: values.email?.trim() || null,
    phone: values.phone?.trim() || null,
    description: values.description?.trim() || null,
  })

  const submit = (values: DeptFormValues) => {
    const body = toBody(values)
    if (dialog.mode === 'edit' && dialog.dept) {
      update.mutate(
        { id: dialog.dept.id, body: { ...body, status: values.status } },
        { onSuccess: close },
      )
    } else {
      create.mutate(body, { onSuccess: close })
    }
  }

  const confirmDelete = (dept: Dept) =>
    modal.confirm({
      title: `删除部门「${dept.name}」？`,
      content: '将一并删除其下所有子部门；子树内存在用户时无法删除。',
      okButtonProps: { danger: true },
      onOk: () => remove.mutateAsync(dept.id),
    })

  const pending = create.isPending || update.isPending

  return (
    <div>
      <DeptToolbar keyword={keyword} onKeywordChange={setKeyword} onCreate={() => openCreate()} />
      <Platform
        desktop={
          <DeptTable
            nodes={nodes}
            loading={isLoading}
            error={error}
            onView={openView}
            onEdit={openEdit}
            onCreateChild={openCreate}
            onDelete={confirmDelete}
            statusPendingId={setStatus.isPending ? setStatus.variables?.id : undefined}
            onStatusChange={(dept, status) => setStatus.mutate({ id: dept.id, status })}
          />
        }
        mobile={
          <DeptTreeList
            nodes={nodes}
            loading={isLoading}
            error={error}
            onView={openView}
            onEdit={openEdit}
            onCreateChild={openCreate}
            onDelete={confirmDelete}
          />
        }
      />
      {dialog.mode === 'view' ? (
        <DeptDetailDrawer open={dialog.open} deptId={dialog.dept?.id} onClose={close} />
      ) : (
        <DeptFormDialog
          open={dialog.open}
          mode={dialog.mode}
          dept={dialog.dept}
          parentId={dialog.parentId}
          excludeIds={excludeIds}
          pending={pending}
          onSubmit={submit}
          onClose={close}
        />
      )}
    </div>
  )
}
