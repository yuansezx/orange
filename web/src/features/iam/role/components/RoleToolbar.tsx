import { Button, Input, Space } from 'antd'

import { RecycleModeSwitch } from '../../components/RecycleModeSwitch'

interface Props {
  keyword: string
  recycleMode: boolean
  onKeywordChange: (keyword: string) => void
  onRecycleModeChange: (recycleMode: boolean) => void
  onCreate: () => void
}

/** 【共用层】角色工具栏：名称/标识过滤（客户端）+ 视图切换 + 新建。 */
export function RoleToolbar({
  keyword,
  recycleMode,
  onKeywordChange,
  onRecycleModeChange,
  onCreate,
}: Props) {
  return (
    <Space style={{ display: 'flex', marginBottom: 16, flexWrap: 'wrap' }} size={12}>
      <RecycleModeSwitch value={recycleMode} onChange={onRecycleModeChange} />
      <Input
        allowClear
        value={keyword}
        placeholder="搜索 名称 / 标识"
        style={{ width: 240, maxWidth: '100%' }}
        onChange={(event) => onKeywordChange(event.target.value)}
      />
      {!recycleMode && (
        <Button type="primary" onClick={onCreate}>
          新建角色
        </Button>
      )}
    </Space>
  )
}
