import { useQuery } from '@tanstack/react-query'
import { Alert, Descriptions, Spin, Tag } from 'antd'

import { DetailDrawer } from '@shared/ui'

import { auditItems } from '../../components/auditItems'
import { DATA_SCOPE_LABELS, STATUS_COLORS, STATUS_LABELS } from '../../constants'
import { getRoleDetail } from '../api/roleApi'
import { PermissionTree } from './PermissionTree'

interface Props {
  open: boolean
  roleId?: string
  onClose: () => void
}

/** 角色详情（只读）——独立展示组件，**不复用编辑表单**。进详情时拉 `GET /roles/{id}/detail`。 */
export function RoleDetailDrawer({ open, roleId, onClose }: Props) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['role-detail', roleId],
    queryFn: () => getRoleDetail(roleId as string),
    enabled: open && !!roleId,
  })

  return (
    <DetailDrawer
      open={open}
      title={data ? `角色详情 · ${data.name}` : '角色详情'}
      onClose={onClose}
    >
      {isLoading ? (
        <Spin />
      ) : error ? (
        <Alert type="error" showIcon message={error.message} />
      ) : data ? (
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="角色标识">{data.code}</Descriptions.Item>
          <Descriptions.Item label="名称">{data.name}</Descriptions.Item>
          <Descriptions.Item label="数据范围">
            {DATA_SCOPE_LABELS[data.data_scope]}
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={STATUS_COLORS[data.status]}>{STATUS_LABELS[data.status]}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="描述">{data.description || '-'}</Descriptions.Item>
          {data.dept_refs.length > 0 && (
            <Descriptions.Item label="数据范围部门">
              {data.dept_refs.map((ref) => (
                <div key={ref.id}>{ref.path}</div>
              ))}
            </Descriptions.Item>
          )}
          <Descriptions.Item label="权限">
            <PermissionTree value={data.permission_ids} readOnly />
          </Descriptions.Item>
          {auditItems(data)}
        </Descriptions>
      ) : null}
    </DetailDrawer>
  )
}
