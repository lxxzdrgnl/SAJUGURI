'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { parseThemePref, THEME_COLOR, THEME_COOKIE, THEME_COOKIE_MAX_AGE } from '@/lib/theme'
import type { ThemePref } from '@/lib/theme'

const OPTIONS: { value: ThemePref; key: 'themeLight' | 'themeDark' | 'themeSystem' }[] = [
  { value: 'light', key: 'themeLight' },
  { value: 'dark', key: 'themeDark' },
  { value: 'system', key: 'themeSystem' },
]

function readPref(): ThemePref {
  if (typeof document === 'undefined') return 'system'
  const m = document.cookie.match(new RegExp(`(?:^|;\\s*)${THEME_COOKIE}=([^;]*)`))
  return parseThemePref(m?.[1])
}

/** 모드를 즉시 반영 — SSR이 다음 접속부터 같은 값을 박도록 쿠키(1년)도 쓴다. */
function applyPref(pref: ThemePref) {
  try {
    document.cookie = `${THEME_COOKIE}=${pref}; path=/; max-age=${THEME_COOKIE_MAX_AGE}; samesite=lax`
  } catch {
    /* 쿠키 불가 환경 무시 */
  }
  const root = document.documentElement
  if (pref === 'system') delete root.dataset.theme
  else root.dataset.theme = pref

  // 브라우저 크롬 색도 맞춘다 (SSR 메타의 content만 갱신 — iOS는 새로 만든 메타를 무시)
  const osDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  document.querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]').forEach((meta) => {
    const media = meta.getAttribute('media')
    let mode: 'light' | 'dark'
    if (pref !== 'system') mode = pref
    else if (media) mode = media.includes('dark') ? 'dark' : 'light'
    else mode = osDark ? 'dark' : 'light'
    meta.setAttribute('content', THEME_COLOR[mode])
  })
}

/** 드로어의 화면 모드 선택 — 라이트 / 다크 / 시스템 */
export default function ThemeToggle() {
  const t = useTranslations('drawer')
  const [pref, setPref] = useState<ThemePref>(readPref)

  function choose(next: ThemePref) {
    setPref(next)
    applyPref(next)
  }

  return (
    <div className="mb-3">
      <p id="theme-toggle-label" className="mb-2 text-xs font-extrabold text-c-text-sub">
        {t('theme')}
      </p>
      <div role="radiogroup" aria-labelledby="theme-toggle-label" className="flex gap-2">
        {OPTIONS.map((o) => {
          const active = pref === o.value
          return (
            <button
              key={o.value}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => choose(o.value)}
              className={
                'h-10 flex-1 rounded-pill text-[13px] font-extrabold transition-opacity ' +
                (active
                  ? 'bg-c-accent text-c-on-accent'
                  : 'border border-c-line bg-c-surface text-c-text-sub hover:opacity-80')
              }
            >
              {t(o.key)}
            </button>
          )
        })}
      </div>
    </div>
  )
}
