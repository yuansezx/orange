import { Segmented } from 'antd'

interface Props {
  value: boolean
  onChange: (recycleMode: boolean) => void
}

/** 正常 / 回收站 视图切换（各页各自入口）。 */
export function RecycleModeSwitch({ value, onChange }: Props) {
  return (
    <Segmented
      value={value ? 'recycle' : 'normal'}
      options={[
        { label: '正常', value: 'normal' },
        { label: '回收站', value: 'recycle' },
      ]}
      onChange={(next) => onChange(next === 'recycle')}
    />
  )
}
