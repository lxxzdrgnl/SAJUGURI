'use client'

import { useEffect, useId, useRef } from 'react'
import { useTranslations } from 'next-intl'
import type { Product } from '@sajuguri/core'
import type { ProfileResponse } from '@sajuguri/api-client'
import { Link } from '@/i18n/navigation'
import { buttonClass } from '@/components/ui/Button'
import { useSheetTransition } from '@/lib/hooks/useSheetTransition'
import { trackProductView } from '@/lib/products/track'
import { posterTone } from '@/lib/products/posterTone'

/** "곧 나와요" 안내 바텀시트 — 지금은 같은 고민을 구리구리 상담으로 넘긴다. */
export default function ComingSoonSheet({
  product,
  open,
  onClose,
  profile = null,
}: {
  product: Product
  open: boolean
  onClose: () => void
  profile?: ProfileResponse | null
}) {
  const t = useTranslations('home.soon')
  const tp = useTranslations('products')
  const { mounted, visible, onTransitionEnd } = useSheetTransition(open)
  const panelRef = useRef<HTMLDivElement>(null)
  const titleId = useId()

  // Esc로 닫기
  useEffect(() => {
    if (!open) return
    const onEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onEsc)
    return () => document.removeEventListener('keydown', onEsc)
  }, [open, onClose])

  // 열려 있는 동안 배경 스크롤 잠금
  useEffect(() => {
    if (!mounted) return
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = prev
    }
  }, [mounted])

  // 열리면 주 버튼으로 포커스, 닫히면 원래 자리로
  useEffect(() => {
    if (!open || !visible) return
    const prev = document.activeElement as HTMLElement | null
    panelRef.current?.querySelector<HTMLElement>('a[href]')?.focus()
    return () => prev?.focus?.()
  }, [open, visible])

  if (!mounted) return null

  const title = tp(`${product.id}.title`)

  // 조상에 transform이 없는 자리(ProductLink 형제)에 렌더되므로 fixed가 뷰포트 기준으로 잡힌다
  return (
    <div className="fixed inset-0 z-40">
      <div
        aria-hidden="true"
        onClick={onClose}
        onTransitionEnd={onTransitionEnd}
        className={`absolute inset-0 bg-c-scrim transition-opacity duration-(--motion-duration-fade) ${
          visible ? 'opacity-100' : 'opacity-0'
        }`}
      />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={`absolute inset-x-0 bottom-0 z-50 mx-auto max-w-[640px] rounded-t-[28px] bg-c-bg px-5 pb-[calc(1.25rem+env(safe-area-inset-bottom))] pt-3 text-c-text transition-transform duration-(--motion-duration-sheet) ease-(--motion-ease-drawer) ${
          visible ? 'translate-y-0' : 'translate-y-full'
        }`}
      >
        <span aria-hidden="true" className="mx-auto mb-5 block h-1 w-10 rounded-pill bg-c-line" />
        <div className="flex items-center gap-4">
          <span className={`flex h-20 w-20 shrink-0 items-center justify-center rounded-card ${posterTone(product)}`}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={product.art} alt="" width={64} height={64} className="h-16 w-16 object-contain" />
          </span>
          <div className="min-w-0">
            <span className="inline-block rounded-pill bg-c-surface-soft px-2.5 py-0.5 text-xs font-bold text-c-text-sub">
              {t('badge')}
            </span>
            <h2 id={titleId} className="mt-1.5 break-keep font-display text-2xl font-normal leading-tight">
              {title}
            </h2>
          </div>
        </div>
        <p className="mt-4 break-keep text-[15px] leading-relaxed text-c-text-sub">{t('body')}</p>
        <div className="mt-6 flex flex-col gap-2">
          <Link
            href={`/chat?topic=${product.id}`}
            onClick={() => trackProductView('guriguri_counsel', profile)}
            className={`${buttonClass('primary', 'md')} h-12 w-full text-[15px]`}
          >
            {t('cta')}
          </Link>
          <button type="button" onClick={onClose} className={`${buttonClass('ghost', 'md')} w-full text-c-text-sub`}>
            {t('close')}
          </button>
        </div>
      </div>
    </div>
  )
}
