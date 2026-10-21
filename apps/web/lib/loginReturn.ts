const KEY = 'loginReturnTo'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
export const GOOGLE_LOGIN_URL = `${API_URL}/api/auth/google?client=web`

/** 같은 사이트 상대 경로만 허용 (오픈 리다이렉트 방지) */
export function isSafeReturnPath(path: unknown): path is string {
  if (typeof path !== 'string' || !path.startsWith('/')) return false
  if (path.startsWith('//') || path.startsWith('/\\')) return false
  if (/[\\\u0000-\u001f]/.test(path)) return false
  return !/^[a-z][a-z0-9+.-]*:/i.test(path)
}

/** 로그인 직전 현재 화면 경로(언어 프리픽스 포함)를 저장 */
export function saveReturnTo(path: string): void {
  try {
    sessionStorage.setItem(KEY, path)
  } catch {
    /* 저장 불가 환경에서는 홈으로 폴백 */
  }
}

/** 저장된 경로를 꺼내며 지운다. 안전하지 않으면 null */
export function consumeReturnTo(): string | null {
  try {
    const v = sessionStorage.getItem(KEY)
    sessionStorage.removeItem(KEY)
    return isSafeReturnPath(v) ? v : null
  } catch {
    return null
  }
}

export function saveCurrentLocation(): void {
  saveReturnTo(window.location.pathname + window.location.search)
}
