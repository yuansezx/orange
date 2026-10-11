const TOKEN_KEY = 'orange.token'

/** 令牌存取（占位实现：localStorage）。后端就绪后接入登录/刷新流程再定策略。 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}
