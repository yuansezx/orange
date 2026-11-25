import { Alert, Spin } from 'antd'

import { DetailDrawer } from '@shared/ui'

import { useAppLogText } from '../hooks/useAppLogText'
import type { AppLogFile } from '../types'

interface Props {
  open: boolean
  file: AppLogFile | null
  onClose: () => void
}

/** 归档日志文本查看（纯文本，不做解析）。 */
export function AppLogViewerDrawer({ open, file, onClose }: Props) {
  const { data, isLoading, error } = useAppLogText(file?.key ?? null, open)

  return (
    <DetailDrawer open={open} title={file?.filename ?? '查看日志'} onClose={onClose}>
      {isLoading && <Spin />}
      {error && <Alert type="error" message={error.message} showIcon />}
      {data !== undefined && (
        <pre
          style={{
            margin: 0,
            maxHeight: '70vh',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-all',
            fontSize: 12,
            lineHeight: 1.6,
          }}
        >
          {data}
        </pre>
      )}
    </DetailDrawer>
  )
}
