import { defineStore } from 'pinia'

interface AuthUser {
  id: number
  email: string
  role: string
  provider: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const user = ref<AuthUser | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  function setTokens(accessToken: string, rt: string) {
    token.value = accessToken
    refreshToken.value = rt
    if (import.meta.client) {
      localStorage.setItem('auth_token', accessToken)
      localStorage.setItem('refresh_token', rt)
    }
  }

  /** 하위 호환성 — access token만 설정 */
  function setToken(t: string) {
    token.value = t
    if (import.meta.client) localStorage.setItem('auth_token', t)
  }

  function logout() {
    // 서버에 로그아웃 요청 (fire-and-forget)
    if (token.value) {
      $fetch('/api/auth/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token.value}` },
      }).catch(() => {})
    }
    token.value = null
    refreshToken.value = null
    user.value = null
    if (import.meta.client) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
    }
  }

  /** Access Token 만료 시 Refresh Token으로 재발급. 실패 시 로그아웃. */
  async function _refresh(): Promise<boolean> {
    const rt = refreshToken.value
    if (!rt) return false
    try {
      const data = await $fetch<{ access_token: string; refresh_token: string }>(
        '/api/auth/refresh',
        { method: 'POST', body: { refresh_token: rt } },
      )
      setTokens(data.access_token, data.refresh_token)
      return true
    } catch {
      logout()
      return false
    }
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const data = await $fetch<AuthUser>('/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      user.value = data
    } catch (err: unknown) {
      // 401이면 refresh 시도
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 401) {
        const ok = await _refresh()
        if (ok) await fetchMe()
      } else {
        logout()
      }
    }
  }

  function init() {
    if (!import.meta.client) return
    const savedToken = localStorage.getItem('auth_token')
    const savedRefresh = localStorage.getItem('refresh_token')
    if (savedToken) {
      token.value = savedToken
      if (savedRefresh) refreshToken.value = savedRefresh
      fetchMe()
    }
  }

  /** 인증이 필요한 fetch — 401 시 자동 refresh 후 1회 재시도 */
  async function authFetch<T>(url: string, opts: Parameters<typeof $fetch>[1] = {}): Promise<T> {
    const makeHeaders = () => ({ ...(opts.headers ?? {}), Authorization: `Bearer ${token.value}` })
    try {
      return await $fetch<T>(url, { ...opts, headers: makeHeaders() })
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 401) {
        const ok = await _refresh()
        if (ok) return await $fetch<T>(url, { ...opts, headers: makeHeaders() })
      }
      throw err
    }
  }

  return { token, refreshToken, user, isLoggedIn, setTokens, setToken, logout, fetchMe, init, authFetch }
})
