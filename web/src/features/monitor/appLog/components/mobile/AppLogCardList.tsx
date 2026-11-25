import { Button, ErrorBlock, List } from 'antd-mobile'

import { formatBytes } from '../../constants'
import type { AppLogFile } from '../../types'

interface Props {
  files: AppLogFile[]
  loading: boolean
  error: Error | null
  onView: (file: AppLogFile) => void
  onDownload: (file: AppLogFile) => void
}

/** 【分叉档 · 移动】归档日志卡片列表。 */
export function AppLogCardList({ files, loading, error, onView, onDownload }: Props) {
  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  return (
    <List>
      {files.map((file) => (
        <List.Item
          key={file.key}
          description={`${file.log_date} · ${formatBytes(file.size)}`}
          extra={
            <Button
              size="mini"
              onClick={(event) => {
                event.stopPropagation()
                onDownload(file)
              }}
            >
              下载
            </Button>
          }
          onClick={() => onView(file)}
        >
          {file.filename}
        </List.Item>
      ))}
      {loading && files.length === 0 && <List.Item>加载中…</List.Item>}
      {!loading && files.length === 0 && <List.Item>暂无归档日志</List.Item>}
    </List>
  )
}
