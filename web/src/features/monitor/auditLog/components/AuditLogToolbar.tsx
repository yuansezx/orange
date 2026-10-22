import { Button, DatePicker, Input, Select, Space } from 'antd'

import type { AuditLogFilters, AuditResult } from '../types'

const RESULT_OPTIONS = [
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failure' },
]

interface Props {
  value: AuditLogFilters
  onChange: (value: AuditLogFilters) => void
  onReset: () => void
}

/** 审计日志筛选：模块 / 资源 / 动作 / 结果 / 时间范围。 */
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
