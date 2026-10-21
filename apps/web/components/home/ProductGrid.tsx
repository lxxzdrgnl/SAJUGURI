import { useTranslations } from 'next-intl'
import type { Product } from '@sajuguri/core'
import PosterCard from './PosterCard'
import ProductLink from './ProductLink'
import { PRESS } from './cardStyles'

/** 카테고리 필터 결과 — 포스터 2열 그리드 */
export default function ProductGrid({
  products,
}: {
  products: Product[]
}) {
  const t = useTranslations('home.grid')

  if (products.length === 0) {
    return <p className="py-16 text-center text-sm text-c-text-sub">{t('empty')}</p>
  }

  return (
    <ul className="grid grid-cols-2 gap-3">
      {products.map((product) => (
        <li key={product.id}>
          <ProductLink product={product} className={PRESS}>
            <PosterCard product={product} />
          </ProductLink>
        </li>
      ))}
    </ul>
  )
}
