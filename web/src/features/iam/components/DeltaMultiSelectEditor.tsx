import { Button, Select } from 'antd'
import { useState } from 'react'

interface Props {
  /** 打开时的已选集合（保存时据此算增量）。 */
  initialIds: string[]
  options: { value: string; label: string; disabled?: boolean }[]
  placeholder: string
  pending: boolean
  onSubmit: (add: string[], remove: string[]) => void
  onCancel: () => void
}

/**
 * 增量多选编辑器：只把「本次新增 / 本次移除」交给调用方。
 * 用户↔角色两个方向共用，避免各自重复算集合差。
 */
export function DeltaMultiSelectEditor({
  initialIds,
  options,
  placeholder,
  pending,
  onSubmit,
  onCancel,
}: Props) {
  const [selected, setSelected] = useState<string[]>(initialIds)

  const handleSave = () => {
    const add = selected.filter((id) => !initialIds.includes(id))
    const remove = initialIds.filter((id) => !selected.includes(id))
    onSubmit(add, remove)
  }

  return (
    <div>
      <Select
        mode="multiple"
        value={selected}
        onChange={setSelected}
        options={options}
        placeholder={placeholder}
        optionFilterProp="label"
        showSearch
        style={{ width: '100%' }}
      />
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 16 }}>
        <Button onClick={onCancel}>取消</Button>
        <Button type="primary" loading={pending} onClick={handleSave}>
          保存
        </Button>
      </div>
    </div>
  )
}
