import { useQuery } from '@tanstack/react-query'
import { Alert, Descriptions, Spin, Tag } from 'antd'

import { auditItems } from '../../components/auditItems'
import { DetailDrawer } from '../../components/DetailDrawer'
import { STATUS_COLORS, STATUS_LABELS } from '../../constants'
import { getDeptDetail } from '../api/deptApi'

interface Props {
  open: boolean
  deptId?: string
  onClose: () => void
}

/** 部门详情（只读）——独立展示组件，**不复用编辑表单**。进详情时拉 `GET /depts/{id}/detail`。 */
export function DeptDetailDrawer({ open, deptId, onClose }: Props) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dept-detail', deptId],
    queryFn: () => getDeptDetail(deptId as string),
    enabled: open && !!deptId,
  })

  return (
    <DetailDrawer
      open={open}
      title={data ? `部门详情 · ${data.name}` : '部门详情'}
      onClose={onClose}
    >
      {isLoading ? (
        <Spin />
      ) : error ? (
        <Alert type="error" showIcon message={error.message} />
      ) : data ? (
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="部门名称">{data.name}</Descriptions.Item>
          <Descriptions.Item label="上级部门">{data.parent?.path ?? '（顶级部门）'}</Descriptions.Item>
          <Descriptions.Item label="负责人">
            {data.leader_nickname || data.leader_username || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="邮箱">{data.email || '-'}</Descriptions.Item>
          <Descriptions.Item label="手机号">{data.phone || '-'}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={STATUS_COLORS[data.status]}>{STATUS_LABELS[data.status]}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="描述">{data.description || '-'}</Descriptions.Item>
          {auditItems(data)}
        </Descriptions>
      ) : null}
    </DetailDrawer>
  )
}
