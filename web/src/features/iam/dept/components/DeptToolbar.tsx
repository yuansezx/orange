import { Button, Input, Space } from 'antd'

interface Props {
  keyword: string
  onKeywordChange: (keyword: string) => void
  onCreate: () => void
}

/** 【共用层】部门工具栏：名称过滤（客户端）+ 新建。 */
export function DeptToolbar({ keyword, onKeywordChange, onCreate }: Props) {
  return (
    <Space style={{ display: 'flex', marginBottom: 16, flexWrap: 'wrap' }} size={12}>
      <Input
        allowClear
        value={keyword}
        placeholder="搜索部门名称"
        style={{ width: 240, maxWidth: '100%' }}
        onChange={(event) => onKeywordChange(event.target.value)}
      />
      <Button type="primary" onClick={onCreate}>
        新建部门
      </Button>
    </Space>
  )
}
