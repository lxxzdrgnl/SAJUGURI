'use client'

import { useEffect, useRef } from 'react'
import { useTranslations } from 'next-intl'
import type { MeResponse, ProfileResponse } from '@sajuguri/api-client'
import { Link, usePathname } from '@/i18n/navigation'
import LanguageToggleInline from '@/components/my/LanguageToggleInline'
import LogoutButton from '@/components/my/LogoutButton'
import { useSheetTransition } from '@/lib/hooks/useSheetTransition'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const GOOGLE_LOGIN_URL = `${API_URL}/api/auth/google?client=web`

const FOCUSABLE = 'a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])'

/** 오른쪽 슬라이드 메뉴 — 딤 클릭·Esc로 닫힘, 포커스 트랩. */
export default function Drawer({
  open,
  onClose,
  user,
}: {
  open: boolean
  onClose: () => void
  user: MeResponse | null
  profiles?: ProfileResponse[]
}) {
  const t = useTranslations('drawer')
  const pathname = usePathname()
  const { mounted, visible, onTransitionEnd } = useSheetTransition(open)
  const panelRef = useRef<HTMLDivElement>(null)

  // 이동하면 닫는다
  useEffect(() => {
    onClose()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname])

  // 열릴 때 포커스 이동, 닫힐 때 원래 위치로 복귀
  useEffect(() => {
    if (!open || !visible) return
    const prev = document.activeElement as HTMLElement | null
    panelRef.current?.querySelector<HTMLElement>(FOCUSABLE)?.focus()
    return () => prev?.focus?.()
  }, [open, visible])

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Escape') {
      e.stopPropagation()
      onClose()
      return
    }
    if (e.key !== 'Tab') return
    const els = panelRef.current?.querySelectorAll<HTMLElement>(FOCUSABLE)
    if (!els || els.length === 0) return
    const first = els[0]
    const last = els[els.length - 1]
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault()
      last.focus()
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault()
      first.focus()
    }
  }

  if (!mounted) return null

  const itemClass =
    'flex h-12 items-center rounded-card px-3 text-[15px] font-extrabold text-c-text hover:bg-c-surface-soft'

  return (
    <div className="fixed inset-0 z-40" onKeyDown={onKeyDown}>
      <div
        aria-hidden="true"
        onClick={onClose}
        onTransitionEnd={onTransitionEnd}
        className={`absolute inset-0 bg-c-text/40 transition-opacity duration-(--motion-duration-fade) ${
          visible ? 'opacity-100' : 'opacity-0'
        }`}
      />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-label={t('profile')}
        className={`absolute inset-y-0 right-0 z-50 flex w-[min(80vw,320px)] flex-col gap-1 overflow-y-auto bg-c-bg px-3 pb-[calc(1rem+env(safe-area-inset-bottom))] pt-[calc(0.75rem+env(safe-area-inset-top))] transition-transform duration-(--motion-duration-sheet) ease-(--motion-ease-out) ${
          visible ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <button
          type="button"
          onClick={onClose}
          aria-label={t('close')}
          className="mb-2 flex h-10 w-10 items-center justify-center self-end rounded-pill text-c-text hover:bg-c-surface-soft"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M6 6 L18 18 M18 6 L6 18" />
          </svg>
        </button>
        {user ? (
          <Link href="/my" className={itemClass}>{t('profile')}</Link>
        ) : (
          <a href={GOOGLE_LOGIN_URL} className={itemClass}>{t('login')}</a>
        )}
        <Link href="/manse" className={itemClass}>{t('manse')}</Link>
        <Link href="/my/history" className={itemClass}>{t('archive')}</Link>
        <div className="mt-4 px-1">
          <LanguageToggleInline />
        </div>
        {user && (
          <div className="mt-2 px-1">
            <LogoutButton />
          </div>
        )}
      </div>
    </div>
  )
}
