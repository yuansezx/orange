import { Button, Collapse, ErrorBlock, List, Switch, Tag } from 'antd-mobile'

import { STATUS_LABELS } from '../../../constants'
import type { Status } from '../../../types'
import { SOURCE_LABELS } from '../../constants'
import type { Resource, ResourcePermission } from '../../types'

interface Props {
  resources: Resource[]
  loading: boolean
  error: Error | null
  recycleMode: boolean
  statusPendingId?: string
  permissionStatusPendingId?: string
  onEdit: (resource: Resource) => void
  onDelete: (resource: Resource) => void
  onRestore: (resource: Resource) => void
  onHardDelete: (resource: Resource) => void
  onStatusChange: (resource: Resource, status: Status) => void
  onCreatePermission: (resource: Resource) => void
  onEditPermission: (resource: Resource, permission: ResourcePermission) => void
  onDeletePermission: (resource: Resource, permission: ResourcePermission) => void
  onPermissionStatusChange: (
    resource: Resource,
    permission: ResourcePermission,
    status: Status,
  ) => void
}

function sourceTag(source: Resource['resource_type']) {
  return (
    <Tag color={source === 'system' ? 'primary' : 'success'}>{SOURCE_LABELS[source]}</Tag>
  )
}

/** 【分叉档 · 移动】资源折叠列表；SYSTEM 只读，CUSTOM 提供编辑/删除/权限管理。 */
export function ResourceCardList({
  resources,
  loading,
  error,
  recycleMode,
  statusPendingId,
  permissionStatusPendingId,
  onEdit,
  onDelete,
  onRestore,
  onHardDelete,
  onStatusChange,
  onCreatePermission,
  onEditPermission,
  onDeletePermission,
  onPermissionStatusChange,
}: Props) {
  if (error) {
    return <ErrorBlock status="default" title="加载失败" description={error.message} />
  }

  if (!loading && resources.length === 0) {
    return <List><List.Item>暂无资源</List.Item></List>
  }

  return (
    <Collapse>
      {resources.map((resource) => {
        const isSystem = resource.resource_type === 'system'
        return (
          <Collapse.Panel
            key={resource.id}
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                <span style={{ fontWeight: 600 }}>{resource.name}</span>
                <span style={{ color: '#999' }}>{resource.key}</span>
                {sourceTag(resource.resource_type)}
                <Tag color={resource.status === 'active' ? 'success' : 'default'}>
                  {STATUS_LABELS[resource.status]}
                </Tag>
              </div>
            }
          >
            {resource.description && (
              <div style={{ color: '#666', marginBottom: 8 }}>{resource.description}</div>
            )}

            {!recycleMode && !isSystem && (
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
                <span>状态</span>
                <Switch
                  checked={resource.status === 'active'}
                  loading={statusPendingId === resource.id}
                  onChange={(checked) => onStatusChange(resource, checked ? 'active' : 'disabled')}
                />
              </div>
            )}

            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
              {isSystem ? (
                <span style={{ color: '#999' }}>系统资源由代码维护</span>
              ) : recycleMode ? (
                <>
                  <Button size="mini" onClick={() => onRestore(resource)}>
                    恢复
                  </Button>
                  <Button size="mini" color="danger" fill="outline" onClick={() => onHardDelete(resource)}>
                    彻底删除
                  </Button>
                </>
              ) : (
                <>
                  <Button size="mini" onClick={() => onEdit(resource)}>
                    编辑
                  </Button>
                  <Button size="mini" color="danger" fill="outline" onClick={() => onDelete(resource)}>
                    删除
                  </Button>
                </>
              )}
              {!recycleMode && (
                <Button size="mini" color="primary" fill="outline" onClick={() => onCreatePermission(resource)}>
                  新增权限
                </Button>
              )}
            </div>

            <List header="权限">
              {resource.permissions.length === 0 && <List.Item>暂无权限</List.Item>}
              {resource.permissions.map((permission) => {
                const isSystemPermission = permission.permission_type === 'system'
                const deleted = Boolean(permission.deleted_at)
                return (
                  <List.Item
                    key={permission.id}
                    description={permission.key}
                    extra={
                      !recycleMode && !isSystemPermission && !deleted ? (
                        <Switch
                          checked={permission.status === 'active'}
                          loading={permissionStatusPendingId === permission.id}
                          onChange={(checked) =>
                            onPermissionStatusChange(
                              resource,
                              permission,
                              checked ? 'active' : 'disabled',
                            )
                          }
                        />
                      ) : (
                        <Tag color={deleted ? 'default' : permission.status === 'active' ? 'success' : 'default'}>
                          {deleted ? '已删除' : STATUS_LABELS[permission.status]}
                        </Tag>
                      )
                    }
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                      <span>{permission.name}</span>
                      <span style={{ color: '#999' }}>{permission.action}</span>
                      {sourceTag(permission.permission_type)}
                    </div>
                    {!recycleMode && !isSystemPermission && !deleted && (
                      <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
                        <Button size="mini" onClick={() => onEditPermission(resource, permission)}>
                          编辑
                        </Button>
                        <Button
                          size="mini"
                          color="danger"
                          fill="outline"
                          onClick={() => onDeletePermission(resource, permission)}
                        >
                          删除
                        </Button>
                      </div>
                    )}
                  </List.Item>
                )
              })}
            </List>
          </Collapse.Panel>
        )
      })}
    </Collapse>
  )
}
