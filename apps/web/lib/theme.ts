/** 화면 모드 — 라이트/다크/시스템. 기본은 시스템(design.md §3). */
export type ThemePref = 'light' | 'dark' | 'system'

export const THEME_COOKIE = 'theme'

/** 쿠키 수명 1년(초) */
export const THEME_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

/** 쿠키 원문 → 모드. 알 수 없는 값은 'system'. */
export function parseThemePref(raw: string | undefined): ThemePref {
  return raw === 'light' || raw === 'dark' || raw === 'system' ? raw : 'system'
}

/** 브라우저 크롬(theme-color) — 앱 배경 --c-bg와 같은 값 */
export const THEME_COLOR = { light: '#FFFFFF', dark: '#121212' } as const

/** 라디오 그룹 화살표 키 이동 (WAI-ARIA) — 처리 대상 키가 아니면 null. 끝에서 순환한다. */
export function nextRadioIndex(key: string, index: number, count: number): number | null {
  if (key === 'ArrowRight' || key === 'ArrowDown') return (index + 1) % count
  if (key === 'ArrowLeft' || key === 'ArrowUp') return (index - 1 + count) % count
  return null
}
