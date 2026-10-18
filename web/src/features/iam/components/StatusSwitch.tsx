import { Switch, Tooltip } from 'antd'
import type { MouseEvent } from 'react'

import type { Status } from '../types'

interface Props {
  status: Status
  loading?: boolean
  disabled?: boolean
  /** 禁用原因（悬浮提示）；不传则不显示提示。 */
  disabledReason?: string
  onChange: (status: Status) => void
}

/** 列表状态开关（药丸型）——点击不冒泡到行，避免同时触发详情。 */
export function StatusSwitch({ status, loading, disabled, disabledReason, onChange }: Props) {
  const content = (
    <span onClick={(event: MouseEvent) => event.stopPropagation()}>
      <Switch
        checked={status === 'active'}
        checkedChildren="启用"
        unCheckedChildren="停用"
        loading={loading}
        disabled={disabled}
        onChange={(checked) => onChange(checked ? 'active' : 'disabled')}
      />
    </span>
  )
  return disabledReason ? <Tooltip title={disabledReason}>{content}</Tooltip> : content
}
