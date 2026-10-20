import { Button, Input, Segmented, Space } from 'antd'

import { RecycleModeSwitch } from '../../components/RecycleModeSwitch'
import type { RecycleKind } from '../types'

interface Props {
  keyword: string
  recycleMode: boolean
  recycleKind: RecycleKind
  onKeywordChange: (keyword: string) => void
  onRecycleModeChange: (recycleMode: boolean) => void
  onRecycleKindChange: (kind: RecycleKind) => void
  onCreate: () => void
}

/** 资源工具栏：视图切换（正常 / 回收站·资源 / 回收站·权限）+ 关键字过滤 + 新建。 */
export function ResourceToolbar({
  keyword,
  recycleMode,
  recycleKind,
  onKeywordChange,
  onRecycleModeChange,
  onRecycleKindChange,
  onCreate,
}: Props) {
  return (
    <Space style={{ display: 'flex', marginBottom: 16, flexWrap: 'wrap' }} size={12}>
      <RecycleModeSwitch value={recycleMode} onChange={onRecycleModeChange} />
      {recycleMode && (
        <Segmented
          value={recycleKind}
          options={[
            { label: '资源', value: 'resources' },
            { label: '权限', value: 'permissions' },
          ]}
          onChange={(value) => onRecycleKindChange(value as RecycleKind)}
        />
      )}
      <Input
        allowClear
        value={keyword}
        placeholder={recycleKind === 'permissions' ? '搜索 资源 / 动作 / 名称' : '搜索 模块 / 标识 / 名称'}
        style={{ width: 240, maxWidth: '100%' }}
        onChange={(event) => onKeywordChange(event.target.value)}
      />
      {!recycleMode && (
        <Button type="primary" onClick={onCreate}>
          新建资源
        </Button>
      )}
    </Space>
  )
}
