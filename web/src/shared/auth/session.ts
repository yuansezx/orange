type Listener = () => void

let listeners: Listener[] = []

/**
 * 订阅「会话失效」（HTTP 层在 401 时广播）——返回取消订阅函数。
 * 由携带路由/UI 上下文的 React 层订阅，用于「提示 + 跳登录页」。
 */
export function onSessionExpired(listener: Listener): () => void {
  listeners.push(listener)
  return () => {
    listeners = listeners.filter((item) => item !== listener)
  }
}

/** 广播「会话失效」（令牌缺失/失效/过期）。 */
export function emitSessionExpired(): void {
  for (const listener of listeners) listener()
}
