import { Form, Input, Modal } from 'antd'
import { useState } from 'react'

import type { PasswordIssueResult, UserListItem } from '../types'
import { TemporaryPasswordView } from './TemporaryPasswordView'

interface FormValues {
  new_password?: string
}

interface Props {
  user: UserListItem
  onSubmit: (password?: string) => Promise<PasswordIssueResult | null>
  onClose: () => void
}

/**
 * 管理员重置密码。
 * - 手输密码：确认 → 关闭弹窗；
 * - 留空：停在弹窗内展示一次性临时密码（保住用户名上下文），确认按钮延迟 1 秒。
 */
export function ResetPasswordModal({ user, onSubmit, onClose }: Props) {
  const [form] = Form.useForm<FormValues>()
  const [submitting, setSubmitting] = useState(false)
  const [issuedPassword, setIssuedPassword] = useState<string | null>(null)
  const displayName = user.nickname || user.username

  const handleFinish = async (values: FormValues) => {
    const password = values.new_password?.trim() || undefined
    setSubmitting(true)
    try {
      const result = await onSubmit(password)
      if (password || !result?.temporary_password) {
        onClose()
      } else {
        setIssuedPassword(result.temporary_password)
      }
    } catch {
      // 错误提示由 mutation 统一处理，弹窗保留以便重试
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal
      open
      title={`重置密码：${displayName}`}
      okText="重置"
      cancelText="取消"
      confirmLoading={submitting}
      okButtonProps={{ danger: true }}
      onOk={() => form.submit()}
      onCancel={() => {
        if (!issuedPassword) onClose()
      }}
      closable={!issuedPassword}
      maskClosable={!issuedPassword}
      keyboard={!issuedPassword}
      footer={issuedPassword ? null : undefined}
    >
      {issuedPassword ? (
        <TemporaryPasswordView
          username={displayName}
          password={issuedPassword}
          onDone={onClose}
        />
      ) : (
        <Form
          form={form}
          layout="vertical"
          requiredMark={false}
          onFinish={handleFinish}
        >
          <Form.Item
            name="new_password"
            label="新密码"
            extra="留空则自动生成。重置后该用户所有设备下线，下次登录需修改密码。"
            rules={[
              {
                validator: (_, value: string | undefined) =>
                  !value || value.length >= 8
                    ? Promise.resolve()
                    : Promise.reject(new Error('密码长度不能少于 8 位')),
              },
            ]}
          >
            <Input.Password placeholder="留空自动生成" autoComplete="new-password" />
          </Form.Item>
        </Form>
      )}
    </Modal>
  )
}
