import { useQuery } from '@tanstack/react-query'
import { Select, Spin } from 'antd'

import { getUsers } from '../user/api/userApi'

/** 用户目录一次取量（管理台规模小；无按 id 反查端点，故用目录 + 客户端过滤）。 */
const DIRECTORY_SIZE = 100

interface Props {
  value?: string
  onChange?: (value?: string) => void
  placeholder?: string
  allowClear?: boolean
  disabled?: boolean
}

/**
 * 用户选择器（下拉）。
 * label = `昵称 || 用户名`；支持按 label 客户端过滤。
 * 无 `iam:user:read` 权限时取数 403 → 选项为空（字段可选，不影响提交）。
 */
export function UserSelect({
  value,
  onChange,
  placeholder = '选择用户',
  allowClear = true,
  disabled,
}: Props) {
  const { data, isFetching } = useQuery({
    queryKey: ['user-directory', DIRECTORY_SIZE],
    queryFn: () => getUsers({ page: 1, page_size: DIRECTORY_SIZE }),
    staleTime: 5 * 60_000,
  })

  const options = (data?.data ?? []).map((user) => ({
    value: user.id,
    label: user.nickname || user.username,
  }))

  return (
    <Select
      value={value}
      onChange={onChange}
      options={options}
      placeholder={placeholder}
      allowClear={allowClear}
      disabled={disabled}
      showSearch
      optionFilterProp="label"
      loading={isFetching}
      notFoundContent={isFetching ? <Spin size="small" /> : null}
      style={{ width: '100%' }}
    />
  )
}
