import { Button, ErrorBlock, List, Tag } from 'antd-mobile'
import dayjs from 'dayjs'

import { SOURCE_LABELS } from '../../constants'
import type { PermissionListItem } from '../../types'

interface Props {
  permissions: PermissionListItem[]
  loading: boolean
  error: Error | null
  onRestore: (permission: PermissionListItem) => void
  onHardDelete: (permission: PermissionListItem) => void
}

/** 【分叉档 · 移动】权限回收站：资源仍存活的已删权限。 */
export function DeletedPermissionCardList({
  permissions,
  loading,
  error,
  onRestore,
  onHardDelete,
}: Props) {
  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  return (
    <List>
      {permissions.map((permission) => (
        <List.Item key={permission.id}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <span style={{ fontWeight: 600 }}>{permission.name}</span>
            <span style={{ color: '#999' }}>{permission.key}</span>
            <Tag color={permission.permission_type === 'system' ? 'primary' : 'success'}>
              {SOURCE_LABELS[permission.permission_type]}
            </Tag>
          </div>
          <div style={{ color: '#999', fontSize: 12, marginTop: 4 }}>
            {permission.resource_name} · {permission.resource_key} ·{' '}
            {permission.deleted_at
              ? dayjs(permission.deleted_at).format('YYYY-MM-DD HH:mm')
              : '-'}
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
            {permission.permission_type === 'system' ? (
              <span style={{ color: '#999' }}>系统声明由代码维护</span>
            ) : (
              <>
                <Button size="mini" onClick={() => onRestore(permission)}>
                  恢复
                </Button>
                <Button
                  size="mini"
                  color="danger"
                  fill="outline"
                  onClick={() => onHardDelete(permission)}
                >
                  彻底删除
                </Button>
              </>
            )}
          </div>
        </List.Item>
      ))}
      {loading && <List.Item>加载中…</List.Item>}
      {!loading && permissions.length === 0 && <List.Item>暂无已删权限</List.Item>}
    </List>
  )
}
