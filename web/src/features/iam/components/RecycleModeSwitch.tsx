import { Segmented } from 'antd'

import { colorTokens } from '@shared/theme/tokens'

interface Props {
  value: boolean
  onChange: (recycleMode: boolean) => void
}

/** 正常 / 回收站 视图切换（各页各自入口）。 */
export function RecycleModeSwitch({ value, onChange }: Props) {
  return (
    <Segmented
      value={value ? 'recycle' : 'normal'}
      style={{
        background: colorTokens.brandSoft,
        border: `1px solid ${colorTokens.borderSecondary}`,
        padding: 2,
      }}
      options={[
        { label: '正常', value: 'normal' },
        { label: '回收站', value: 'recycle' },
      ]}
      onChange={(next) => onChange(next === 'recycle')}
    />
  )
}
