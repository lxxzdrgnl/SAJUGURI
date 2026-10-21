import type { ReactNode } from 'react'
import type { Viewport } from 'next'
import { NextIntlClientProvider, hasLocale } from 'next-intl'
import { notFound } from 'next/navigation'
import { Noto_Serif_KR, Jua } from 'next/font/google'
import { routing } from '@/i18n/routing'
import AppHeader from '@/components/nav/AppHeader'
import { currentUser, serverAuthApi } from '@/lib/serverAuth'
import { listProfiles } from '@sajuguri/api-client'
import type { MeResponse, ProfileResponse } from '@sajuguri/api-client'
import LocaleBoot from '@/components/LocaleBoot'
import { cookies } from 'next/headers'
import { parseThemePref, THEME_COLOR, THEME_COOKIE } from '@/lib/theme'
import '../globals.css'

// 간지(천간·지지) 명조체 — font-serif(--font-serif)에 한글·한자 세리프 글리프를 공급한다.
// subsets:['latin']은 라틴 글리프만 받아 한글·한자가 고딕으로 폴백됐다.
// 한국어 폰트는 'korean' 서브셋을 직접 못 받으므로 subsets를 비우고 preload:false로 둔다
// (거대한 CJK 글리프를 preload하진 않되 모든 unicode-range @font-face를 포함해 필요 시 로드).
const notoSerifKR = Noto_Serif_KR({
  weight: ['700', '900'],
  variable: '--font-serif-kr',
  display: 'swap',
  preload: false,
})

// 디스플레이 글꼴 주아 — globals.css의 --font-display(Tailwind font-display)가 소비한다.
// Noto_Serif_KR과 같은 이유로 CJK 글리프 preload는 끈다(필요 시 unicode-range로 로드).
const jua = Jua({
  weight: '400',
  variable: '--font-jua',
  display: 'swap',
  preload: false,
})

// metadataBase — og:image(공유 카드 미리보기)·트위터 이미지가 절대 URL로 해석되도록.
// 미설정 시 Next가 localhost:3000으로 해석해 카카오/트위터가 이미지를 못 불러와 미리보기가 깨진다.
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://sajuguri.rheon.kr'

export const metadata = {
  metadataBase: new URL(SITE_URL),
  title: '사주구리',
}

// viewport-fit=cover — iOS 세이프에어리어(노치·홈인디케이터)까지 페이지가 칠해지게.
// 이게 없으면 풀스크린 오버레이(운세 스토리)가 상하 세이프에어리어를 못 덮어
// 기본 배경(청록)이 띠로 남는다. env(safe-area-inset-*)도 이 설정이 있어야 동작.
//
// theme-color 메타는 SSR HTML에 항상 심는다. iOS Safari는 JS로 '새로 생성'한
// theme-color는 크롬 틴트에 반영하지 않지만, '기존' 메타의 content 갱신은 반영한다.
// 값은 앱 배경(--c-bg)과 같게 — 고른 모드를 따르고, 시스템 모드면 미디어별로 둘 다 심는다.
export async function generateViewport(): Promise<Viewport> {
  const pref = parseThemePref((await cookies()).get(THEME_COOKIE)?.value)
  return {
    width: 'device-width',
    initialScale: 1,
    viewportFit: 'cover',
    colorScheme: pref === 'system' ? 'light dark' : pref,
    themeColor:
      pref === 'system'
        ? [
            { media: '(prefers-color-scheme: light)', color: THEME_COLOR.light },
            { media: '(prefers-color-scheme: dark)', color: THEME_COLOR.dark },
          ]
        : THEME_COLOR[pref],
  }
}

/** 헤더용 호출이 백엔드 지연으로 모든 페이지를 붙잡지 않도록 2초 제한 */
function withTimeout<T>(p: Promise<T>, fallback: T, ms = 2000): Promise<T> {
  return Promise.race([p, new Promise<T>((r) => setTimeout(() => r(fallback), ms))])
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: ReactNode
  params: Promise<{ locale: string }>
}) {
  const { locale } = await params
  if (!hasLocale(routing.locales, locale)) notFound()
  // 헤더용 — 백엔드 장애·비로그인이어도 레이아웃은 렌더된다
  let user: MeResponse | null = null
  let profiles: ProfileResponse[] = []
  try {
    user = await withTimeout(currentUser(), null)
    if (user) profiles = await withTimeout(serverAuthApi().then(listProfiles), [])
  } catch {
    user = null
    profiles = []
  }
  const repProfile = profiles.find((p) => p.is_representative) ?? null
  // 화면 모드 — 라이트/다크는 SSR에서 바로 박아 깜빡임이 없다. 시스템이면 속성 없이 CSS 미디어쿼리에 맡긴다.
  // (ThemeToggle이 클라이언트에서 data-theme을 고치므로 html은 suppressHydrationWarning)
  const themePref = parseThemePref((await cookies()).get(THEME_COOKIE)?.value)
  return (
    <html
      lang={locale}
      className={`${notoSerifKR.variable} ${jua.variable}`}
      data-theme={themePref === 'system' ? undefined : themePref}
      suppressHydrationWarning
    >
      <body>
        <NextIntlClientProvider>
          {/* 저장된 언어 선택을 부팅 시 강제 (영어 기기여도 한국어 유지) */}
          <LocaleBoot />
          {/* 모바일 단일 컬럼 — design.md §7 */}
          <AppHeader user={user} repProfile={repProfile} />
          <div className="mx-auto max-w-[640px] px-4 pb-8 pt-2">{children}</div>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}
