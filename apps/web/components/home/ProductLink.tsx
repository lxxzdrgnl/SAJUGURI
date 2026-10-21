'use client'

import { useCallback, useState, type ReactNode } from 'react'
import type { Product } from '@sajuguri/core'
import { Link } from '@/i18n/navigation'
import { trackProductView } from '@/lib/products/track'
import FortuneEntrySheet from '@/components/fortune/FortuneEntrySheet'
import ReportEntrySheet from '@/components/report/ReportEntrySheet'
import ComingSoonSheet from './ComingSoonSheet'
import { useHomeViewer } from './HomeViewer'

/**
 * 상품 진입 래퍼 — 열람 기록 후
 * - 오늘의 운세·사주 리포트: 만세력 선택 시트(생년월일이 있어야 화면이 열린다)
 * - 그 밖의 available: 상품 화면으로 이동
 * - coming_soon: "곧 나와요" 시트
 * children은 phrasing 요소(span)로 구성해야 button 안에서도 유효하다.
 * 눌림 피드백은 호출부가 className으로 정한다 (cardStyles PRESS 참고).
 */
export default function ProductLink({
  product,
  className = '',
  children,
}: {
  product: Product
  className?: string
  children: ReactNode
}) {
  const { profiles, isLoggedIn, repProfile } = useHomeViewer()
  const [open, setOpen] = useState(false)
  const close = useCallback(() => setOpen(false), [])
  const cls = `block text-left ${className}`.trim()

  const usesSheet =
    product.status === 'coming_soon' || product.id === 'daily_fortune' || product.id === 'saju_report'

  if (!usesSheet && product.href) {
    return (
      <Link href={product.href} onClick={() => trackProductView(product.id, repProfile)} className={cls}>
        {children}
      </Link>
    )
  }

  return (
    <>
      <button
        type="button"
        aria-haspopup="dialog"
        onClick={() => {
          trackProductView(product.id, repProfile)
          setOpen(true)
        }}
        className={`${cls} w-full`}
      >
        {children}
      </button>
      {product.id === 'daily_fortune' ? (
        <FortuneEntrySheet open={open} onClose={close} profiles={profiles} isLoggedIn={isLoggedIn} />
      ) : product.id === 'saju_report' ? (
        <ReportEntrySheet open={open} onClose={close} profiles={profiles} isLoggedIn={isLoggedIn} />
      ) : (
        <ComingSoonSheet product={product} open={open} onClose={close} profile={repProfile} />
      )}
    </>
  )
}
