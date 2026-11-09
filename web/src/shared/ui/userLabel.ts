/**
 * 用户身份展示：`username` 是稳定标识，`nickname` 是可长可变的展示名。
 * 列表/审计流只显示 username，不走这里。
 */

/** 选择器：认人优先，`昵称（username）`；缺昵称或与账号相同时只显示账号。 */
export function userChoiceLabel(username?: string | null, nickname?: string | null): string {
  const name = nickname?.trim()
  if (!username) return name || ''
  return name && name !== username ? `${name}（${username}）` : username
}

/** 详情里的单行引用：`username（nickname）`；缺昵称或与账号相同时只显示账号。 */
export function userRefLabel(username?: string | null, nickname?: string | null): string {
  if (!username) return nickname?.trim() || ''
  const name = nickname?.trim()
  return name && name !== username ? `${username}（${name}）` : username
}
