'use client'

import { useCallback, useState, type ReactNode } from 'react'
import type { Product } from '@sajuguri/core'
import type { ProfileResponse } from '@sajuguri/api-client'
import { Link } from '@/i18n/navigation'
import { trackProductView } from '@/lib/products/track'
import ComingSoonSheet from './ComingSoonSheet'

/**
 * 상품 진입 래퍼 — available은 열람 기록 후 상품 화면으로, coming_soon은 "곧 나와요" 시트.
 * children은 phrasing 요소(span)로 구성해야 button 안에서도 유효하다.
 * 눌림 피드백은 호출부가 className으로 정한다 (cardStyles PRESS 참고).
 */
export default function ProductLink({
  product,
  profile = null,
  className = '',
  children,
}: {
  product: Product
  profile?: ProfileResponse | null
  className?: string
  children: ReactNode
}) {
  const [open, setOpen] = useState(false)
  const close = useCallback(() => setOpen(false), [])
  const cls = `block text-left ${className}`.trim()

  if (product.status === 'available' && product.href) {
    return (
      <Link href={product.href} onClick={() => trackProductView(product.id, profile)} className={cls}>
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
          trackProductView(product.id, profile)
          setOpen(true)
        }}
        className={`${cls} w-full`}
      >
        {children}
      </button>
      <ComingSoonSheet product={product} open={open} onClose={close} profile={profile} />
    </>
  )
}
