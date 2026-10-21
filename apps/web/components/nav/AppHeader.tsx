'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import type { MeResponse, ProfileResponse } from '@sajuguri/api-client'
import { Link, usePathname, useRouter } from '@/i18n/navigation'
import Drawer from './Drawer'
import IlganChip from './IlganChip'

const ICON = {
  width: 22,
  height: 22,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
}
const iconBtn =
  'flex h-10 w-10 shrink-0 items-center justify-center rounded-pill text-c-text hover:bg-c-surface-soft'

/**
 * 앱 헤더 — 홈은 로고·일간 칩·검색·메뉴, 하위 화면은 뒤로·로고·메뉴.
 * 운세 스토리 오버레이(z-50)보다 낮고 본문(z-10)보다 높은 z-30.
 * onSearch: Task 10의 SearchSheet 연결 자리 (없으면 검색 버튼을 숨긴다).
 */
export default function AppHeader({
  user,
  repProfile,
  onSearch,
}: {
  user: MeResponse | null
  repProfile: ProfileResponse | null
  onSearch?: () => void
}) {
  const t = useTranslations('nav')
  const pathname = usePathname()
  const router = useRouter()
  const [menuOpen, setMenuOpen] = useState(false)
  const home = pathname === '/'

  function goBack() {
    if (typeof window !== 'undefined' && window.history.length > 1) router.back()
    else router.push('/')
  }

  const logo = (
    <Link href="/" className="font-display text-lg font-normal text-c-text">
      {t('logo')}
    </Link>
  )

  return (
    <>
    <header className="sticky top-0 z-30 mx-auto w-full max-w-[640px] bg-c-bg pt-[env(safe-area-inset-top)]">
      <div className="flex h-14 items-center gap-2 px-3">
        {home ? (
          <>
            {logo}
            <div className="flex min-w-0 flex-1 justify-end">
              <IlganChip profile={repProfile} />
            </div>
            {onSearch && (
              <button type="button" onClick={onSearch} aria-label={t('search')} className={iconBtn}>
                <svg {...ICON}><circle cx="11" cy="11" r="7" /><path d="M20 20 L16 16" /></svg>
              </button>
            )}
          </>
        ) : (
          <>
            <button type="button" onClick={goBack} aria-label={t('back')} className={iconBtn}>
              <svg {...ICON}><path d="M15 5 L8 12 L15 19" /></svg>
            </button>
            <div className="flex-1">{logo}</div>
          </>
        )}
        <button
          type="button"
          onClick={() => setMenuOpen(true)}
          aria-label={t('menu')}
          aria-haspopup="dialog"
          aria-expanded={menuOpen}
          className={iconBtn}
        >
          <svg {...ICON}><path d="M4 7 H20 M4 12 H20 M4 17 H20" /></svg>
        </button>
      </div>
    </header>
    {/* 헤더(z-30) 쌓임 맥락 밖에 둔다 — 본문 z-10 요소 위로 올라오도록 */}
    <Drawer open={menuOpen} onClose={() => setMenuOpen(false)} user={user} />
    </>
  )
}
