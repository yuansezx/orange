import { Alert, DatePicker, Form, Input, Radio, Typography } from 'antd'
import dayjs from 'dayjs'
import type { Dayjs } from 'dayjs'

import { API_KEY_DATA_SCOPE_LABELS } from '../constants'
import { useVisibleDepts } from '../hooks/useApiKeys'
import type { ApiKey, ApiKeyFormValues } from '../types'
import { ScopeCandidateTree } from './ScopeCandidateTree'
import { VisibleDeptMultiSelect } from './VisibleDeptMultiSelect'

interface Props {
  /** 供抽屉底部的原生 submit 按钮 `form=` 关联。 */
  formId: string
  mode: 'create' | 'edit'
  initial?: ApiKey
  onSubmit: (values: ApiKeyFormValues) => void
}

/**
 * API Key 表单字段（新建 / 编辑共用，提交由外层抽屉承担）。
 * 由外层以 `key` 重挂，故用 `initialValues` 初始化即可。
 */
export function ApiKeyForm({ formId, mode, initial, onSubmit }: Props) {
  const [form] = Form.useForm<ApiKeyFormValues>()
  const { data: visibleDepts = [] } = useVisibleDepts()
  const dataScope = Form.useWatch('data_scope_kind', form)
  const expiryMode = Form.useWatch('expiry_mode', form)
  const canCustom = visibleDepts.length > 0
  const keepCustom = canCustom || initial?.data_scope_kind === 'custom'

  const dataScopeOptions = [
    { value: 'all', label: API_KEY_DATA_SCOPE_LABELS.all },
    { value: 'self', label: API_KEY_DATA_SCOPE_LABELS.self },
    ...(keepCustom ? [{ value: 'custom', label: API_KEY_DATA_SCOPE_LABELS.custom }] : []),
  ]

  const expiryOptions = [
    ...(mode === 'create' ? [{ value: 'default', label: '默认 90 天' }] : []),
    { value: 'custom', label: '指定时间' },
    { value: 'never', label: '永久有效' },
  ]

  const initialValues: ApiKeyFormValues =
    mode === 'edit' && initial
      ? {
          name: initial.name,
          scopes: initial.scopes,
          data_scope_kind: initial.data_scope_kind,
          data_scope_dept_ids: initial.data_scope_dept_ids,
          expiry_mode: initial.expires_at ? 'custom' : 'never',
          expires_at: initial.expires_at ? dayjs(initial.expires_at) : null,
        }
      : {
          name: '',
          scopes: [],
          data_scope_kind: 'all',
          data_scope_dept_ids: [],
          expiry_mode: 'default',
          expires_at: null,
        }

  return (
    <Form
      id={formId}
      form={form}
      layout="vertical"
      requiredMark={false}
      initialValues={initialValues}
      onValuesChange={(changed) => {
        if ('data_scope_kind' in changed && changed.data_scope_kind !== 'custom') {
          form.setFieldValue('data_scope_dept_ids', [])
        }
      }}
      onFinish={onSubmit}
    >
      <Form.Item
        name="name"
        label="名称"
        rules={[{ required: true, whitespace: true, message: '请输入名称' }]}
      >
        <Input maxLength={64} placeholder="用于区分多把 key，例如：CI 部署" />
      </Form.Item>

      <Form.Item
        name="scopes"
        label="权限范围"
        rules={[{ required: true, type: 'array', min: 1, message: '至少选择一个权限' }]}
        extra="只能选择你当前拥有的权限；已失权的旧授权在保存时会被移除。"
      >
        <ScopeCandidateTree />
      </Form.Item>

      <Form.Item name="data_scope_kind" label="数据范围" rules={[{ required: true }]}>
        <Radio.Group options={dataScopeOptions} />
      </Form.Item>
      <Typography.Text type="secondary" style={{ display: 'block', marginTop: -16, marginBottom: 16 }}>
        全部数据 = 不额外限制；仅本人 = 只能访问你本人创建的数据。
      </Typography.Text>

      {dataScope === 'custom' && (
        <>
          {!canCustom && (
            <Alert
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
              message="当前没有可见部门，无法使用自定义范围；请改为全部数据或仅本人。"
            />
          )}
          <Form.Item
            name="data_scope_dept_ids"
            label="指定部门"
            extra="已不在你可见范围内的部门会在加载后自动移除。"
            rules={[
              { required: true, type: 'array', min: 1, message: '请选择部门' },
              {
                validator: (_, value: string[] | undefined) =>
                  canCustom && value?.length
                    ? Promise.resolve()
                    : Promise.reject(new Error('当前没有可见部门')),
              },
            ]}
          >
            <VisibleDeptMultiSelect disabled={!canCustom} />
          </Form.Item>
        </>
      )}

      <Form.Item name="expiry_mode" label="有效期" rules={[{ required: true }]}>
        <Radio.Group options={expiryOptions} />
      </Form.Item>
      {expiryMode === 'custom' && (
        <Form.Item
          name="expires_at"
          label="过期时间"
          rules={[
            { required: true, message: '请选择过期时间' },
            {
              validator: (_, value: Dayjs | null | undefined) =>
                !value || value.isAfter(dayjs())
                  ? Promise.resolve()
                  : Promise.reject(new Error('过期时间必须晚于当前时间')),
            },
          ]}
        >
          <DatePicker
            showTime
            style={{ width: '100%' }}
            disabledDate={(date) => date.isBefore(dayjs(), 'day')}
          />
        </Form.Item>
      )}
      {mode === 'create' && expiryMode === 'default' && (
        <Typography.Text type="secondary">未指定时默认 90 天后过期。</Typography.Text>
      )}
    </Form>
  )
}
