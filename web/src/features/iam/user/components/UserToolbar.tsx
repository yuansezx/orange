import { Button, Input, Select, Space } from 'antd'

import { STATUS_OPTIONS, USER_TYPE_OPTIONS } from '../constants'
import type { UserToolbarProps } from '../types'

/**
 * 【共用层】工具栏（搜索 + 状态/类型筛选 + 新建）——两端共用，不放 desktop/ mobile/。
 * 回调 patch 的键即 URL query 参数名（`keyword` / `status` / `user_type`）。
 */
export function UserToolbar({
  keyword,
  status,
  userType,
  onChange,
  onCreate,
}: UserToolbarProps) {
  return (
    <Space style={{ display: 'flex', marginBottom: 16, flexWrap: 'wrap' }} size={12}>
      <Input.Search
        allowClear
        defaultValue={keyword}
        placeholder="搜索 用户名 / 昵称 / 邮箱 / 手机号"
        style={{ width: 280, maxWidth: '100%' }}
        onSearch={(value) => onChange({ keyword: value.trim() || undefined })}
      />
      <Select
        allowClear
        placeholder="状态"
        style={{ width: 110 }}
        value={status}
        options={STATUS_OPTIONS}
        onChange={(value) => onChange({ status: value })}
      />
      <Select
        allowClear
        placeholder="类型"
        style={{ width: 140 }}
        value={userType}
        options={USER_TYPE_OPTIONS}
        onChange={(value) => onChange({ user_type: value })}
      />
      <Button type="primary" onClick={onCreate}>
        新建用户
      </Button>
    </Space>
  )
}
