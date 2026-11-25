import { Alert, Button, Space, Table } from 'antd'
import type { TableProps } from 'antd'
import dayjs from 'dayjs'

import { IconDownload } from '@shared/ui'

import { formatBytes } from '../../constants'
import type { AppLogFile } from '../../types'

interface Props {
  files: AppLogFile[]
  loading: boolean
  error: Error | null
  onView: (file: AppLogFile) => void
  onDownload: (file: AppLogFile) => void
}

/** 【分叉档 · 桌面】归档日志表格。 */
export function AppLogTable({ files, loading, error, onView, onDownload }: Props) {
  if (error) {
    return <Alert type="error" message={error.message} showIcon />
  }

  const columns: TableProps<AppLogFile>['columns'] = [
    { title: '文件名', dataIndex: 'filename', ellipsis: true },
    { title: '日期', dataIndex: 'log_date', width: 120 },
    {
      title: '大小',
      dataIndex: 'size',
      width: 100,
      render: (value: number) => formatBytes(value),
    },
    { title: '实例', dataIndex: 'instance', width: 150, ellipsis: true },
    {
      title: '最后修改',
      dataIndex: 'last_modified',
      width: 170,
      render: (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      render: (_, record) => (
        <Space size={4}>
          <Button type="link" size="small" onClick={() => onView(record)}>
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<IconDownload size={14} />}
            onClick={() => onDownload(record)}
          >
            下载
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <Table<AppLogFile>
      rowKey="key"
      loading={loading}
      columns={columns}
      dataSource={files}
      pagination={false}
      locale={{ emptyText: '暂无归档日志' }}
      scroll={{ x: 'max-content' }}
    />
  )
}
