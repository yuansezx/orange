import { Button, DatePicker, Input, Select, Space } from 'antd'

import { AUTH_METHOD_LABELS } from '../constants'
import type { AuditLogFilters, AuditResult, AuthMethod } from '../types'

const RESULT_OPTIONS = [
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failure' },
]

const AUTH_OPTIONS = (Object.keys(AUTH_METHOD_LABELS) as AuthMethod[]).map((value) => ({
  value,
  label: AUTH_METHOD_LABELS[value],
}))

interface Props {
  value: AuditLogFilters
  onChange: (value: AuditLogFilters) => void
  onReset: () => void
}

/** 审计日志筛选：模块 / 资源 / 动作 / 操作人 / 关键词 / 来源 / 结果 / 时间范围。 */
export function AuditLogToolbar({ value, onChange, onReset }: Props) {
  return (
    <Space style={{ display: 'flex', marginBottom: 16 }} size={12} wrap>
      <Input
        allowClear
        value={value.module}
        placeholder="模块"
        style={{ width: 120 }}
        onChange={(event) => onChange({ ...value, module: event.target.value })}
      />
      <Input
        allowClear
        value={value.resource}
        placeholder="资源"
        style={{ width: 120 }}
        onChange={(event) => onChange({ ...value, resource: event.target.value })}
      />
      <Input
        allowClear
        value={value.action}
        placeholder="动作"
        style={{ width: 120 }}
        onChange={(event) => onChange({ ...value, action: event.target.value })}
      />
      <Input
        allowClear
        value={value.operator}
        placeholder="操作人"
        style={{ width: 140 }}
        onChange={(event) => onChange({ ...value, operator: event.target.value })}
      />
      <Input
        allowClear
        value={value.keyword}
        placeholder="关键词（摘要/目标/错误）"
        style={{ width: 220 }}
        onChange={(event) => onChange({ ...value, keyword: event.target.value })}
      />
      <Select<AuthMethod>
        allowClear
        value={value.authMethod}
        options={AUTH_OPTIONS}
        placeholder="来源"
        style={{ width: 130 }}
        onChange={(authMethod) => onChange({ ...value, authMethod })}
        onClear={() => onChange({ ...value, authMethod: undefined })}
      />
      <Select<AuditResult>
        allowClear
        value={value.result}
        options={RESULT_OPTIONS}
        placeholder="结果"
        style={{ width: 120 }}
        onChange={(result) => onChange({ ...value, result })}
        onClear={() => onChange({ ...value, result: undefined })}
      />
      <DatePicker.RangePicker
        showTime
        value={value.range}
        style={{ maxWidth: '100%' }}
        onChange={(range) =>
          onChange({
            ...value,
            range: range && range[0] && range[1] ? [range[0], range[1]] : null,
          })
        }
      />
      <Button onClick={onReset}>重置</Button>
    </Space>
  )
}
