import { Spin } from 'antd'

export function PageLoading() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
      <Spin />
    </div>
  )
}
