import { useTranslations } from 'next-intl'
import type { Product } from '@sajuguri/core'
import type { ProfileResponse } from '@sajuguri/api-client'
import PosterCard from './PosterCard'
import ProductLink from './ProductLink'
import { PRESS } from './cardStyles'

/** 카테고리 필터 결과 — 포스터 2열 그리드 */
export default function ProductGrid({
  products,
  profile = null,
}: {
  products: Product[]
  profile?: ProfileResponse | null
}) {
  const t = useTranslations('home.grid')

  if (products.length === 0) {
    return <p className="py-16 text-center text-sm text-c-text-sub">{t('empty')}</p>
  }

  return (
    <ul className="grid grid-cols-2 gap-3">
      {products.map((product) => (
        <li key={product.id}>
          <ProductLink product={product} profile={profile} className={PRESS}>
            <PosterCard product={product} />
          </ProductLink>
        </li>
      ))}
    </ul>
  )
}
