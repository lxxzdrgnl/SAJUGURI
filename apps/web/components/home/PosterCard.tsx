import { useTranslations } from 'next-intl'
import type { Product } from '@sajuguri/core'
import { posterTone } from '@/lib/products/posterTone'

/** 3:4 포스터 카드 — 제목 왼쪽 위, 스티커 일러스트 아래 가운데. (span만 사용: 버튼 안에도 들어간다) */
export default function PosterCard({ product }: { product: Product }) {
  const t = useTranslations('products')
  const tSoon = useTranslations('home.soon')

  return (
    <span className={`relative flex aspect-[3/4] w-full flex-col overflow-hidden rounded-card p-4 text-c-text ${posterTone(product)}`}>
      {product.status === 'coming_soon' && (
        <span className="mb-2 self-start rounded-pill bg-c-surface px-2 py-0.5 text-[11px] font-bold text-c-text-sub">
          {tSoon('badge')}
        </span>
      )}
      <span className="block break-keep font-display text-[19px] font-normal leading-[1.2]">
        {t(`${product.id}.title`)}
      </span>
      <span className="mt-1.5 line-clamp-2 break-keep text-xs leading-snug text-c-text-sub">
        {t(`${product.id}.desc`)}
      </span>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={product.art}
        alt=""
        aria-hidden="true"
        width={120}
        height={120}
        loading="lazy"
        className="pointer-events-none absolute bottom-2 left-1/2 h-[40%] w-auto -translate-x-1/2 object-contain"
      />
    </span>
  )
}
