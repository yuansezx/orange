import { Button, Input, Space } from 'antd'

interface Props {
  keyword: string
  onKeywordChange: (keyword: string) => void
  onCreate: () => void
}

/** 【共用层】角色工具栏：名称/标识过滤（客户端）+ 新建。 */
export function RoleToolbar({ keyword, onKeywordChange, onCreate }: Props) {
  return (
    <Space style={{ display: 'flex', marginBottom: 16, flexWrap: 'wrap' }} size={12}>
      <Input
        allowClear
        value={keyword}
        placeholder="搜索 名称 / 标识"
        style={{ width: 240, maxWidth: '100%' }}
        onChange={(event) => onKeywordChange(event.target.value)}
      />
      <Button type="primary" onClick={onCreate}>
        新建角色
      </Button>
    </Space>
  )
}
