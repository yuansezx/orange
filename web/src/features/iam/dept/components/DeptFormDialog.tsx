import { Button, Form, Modal } from 'antd'
import { Popup } from 'antd-mobile'
import { useEffect } from 'react'

import { Platform } from '@shared/platform'

import { DeptForm } from './DeptForm'
import type { Dept, DeptFormValues } from '../types'

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  dept?: Dept
  parentId?: string
  excludeIds?: string[]
  pending: boolean
  onSubmit: (values: DeptFormValues) => void
  onClose: () => void
}

/** 部门表单弹层：同一份 `DeptForm`，桌面 Modal / 移动 Popup（平台分叉收口于此）。 */
export function DeptFormDialog({
  open,
  mode,
  dept,
  parentId,
  excludeIds,
  pending,
  onSubmit,
  onClose,
}: Props) {
  const [form] = Form.useForm<DeptFormValues>()

  useEffect(() => {
    if (!open) return
    if (mode === 'edit' && dept) {
      form.setFieldsValue({
        name: dept.name,
        parent_id: dept.parent_id ?? undefined,
        leader_id: dept.leader_id ?? undefined,
        email: dept.email ?? undefined,
        phone: dept.phone ?? undefined,
        description: dept.description ?? undefined,
        status: dept.status,
      })
    } else {
      form.resetFields()
      form.setFieldsValue({ parent_id: parentId })
    }
  }, [open, mode, dept, parentId, form])

  const submit = async () => {
    const values = await form.validateFields()
    onSubmit(values)
  }

  const title = mode === 'edit' ? '编辑部门' : '新建部门'

  return (
    <Platform
      desktop={
        <Modal
          open={open}
          title={title}
          onOk={submit}
          confirmLoading={pending}
          onCancel={onClose}
          maskClosable={false}
        >
          <DeptForm form={form} mode={mode} excludeIds={excludeIds} />
        </Modal>
      }
      mobile={
        <Popup
          visible={open}
          onMaskClick={onClose}
          bodyStyle={{
            borderTopLeftRadius: 12,
            borderTopRightRadius: 12,
            maxHeight: '90vh',
            overflow: 'auto',
          }}
        >
          <div style={{ padding: 16 }}>
            <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 12 }}>{title}</div>
            <DeptForm form={form} mode={mode} excludeIds={excludeIds} />
            <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
              <Button block onClick={onClose}>
                取消
              </Button>
              <Button block type="primary" loading={pending} onClick={submit}>
                确定
              </Button>
            </div>
          </div>
        </Popup>
      }
    />
  )
}
