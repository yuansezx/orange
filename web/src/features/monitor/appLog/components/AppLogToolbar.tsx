import { Button, DatePicker, Space } from 'antd'

import { usePermission } from '@features/auth'
import { IconRefresh } from '@shared/ui'

import { useAppLogArchive } from '../hooks/useAppLogArchive'
import type { AppLogFilters } from '../types'

interface Props {
  value: AppLogFilters
  onChange: (value: AppLogFilters) => void
  onRefresh: () => void
  refreshing: boolean
}

/** 归档日志筛选：日期范围 / 刷新 / 手动归档。 */
export function AppLogToolbar({ value, onChange, onRefresh, refreshing }: Props) {
  const { can } = usePermission()
  const archive = useAppLogArchive()

  return (
    <Space style={{ display: 'flex', marginBottom: 16 }} size={12} wrap>
      <DatePicker.RangePicker
        value={value.range}
        style={{ maxWidth: '100%' }}
        onChange={(range) =>
          onChange({
            range: range && range[0] && range[1] ? [range[0], range[1]] : null,
          })
        }
      />
      <Button icon={<IconRefresh size={16} />} loading={refreshing} onClick={onRefresh}>
        刷新
      </Button>
      {can('monitor:app_log:archive') && (
        <Button type="primary" loading={archive.isPending} onClick={() => archive.mutate()}>
          手动归档
        </Button>
      )}
    </Space>
  )
}
