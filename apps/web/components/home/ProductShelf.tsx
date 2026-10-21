import { useTranslations } from 'next-intl'
import { getProduct, type Shelf } from '@sajuguri/core'
import PosterCard from './PosterCard'
import ProductLink from './ProductLink'
import { PRESS } from './cardStyles'

/**
 * 맞춤 선반 — 일간 큐레이션 또는 인기 큐레이션. 선반 컨테이너만 가로 스크롤.
 * 큐레이션인 동안 제목에 "많이 본"을 쓰지 않는다(가짜 수치 회피).
 */
export default function ProductShelf({
  shelf,
  stem,
}: {
  shelf: Shelf
  /** 제목에 넣을 일간 표기 (ko: 한글, en: 한자) */
  stem: string | null
}) {
  const t = useTranslations('home.shelf')
  const title = shelf.kind === 'ilgan' && stem ? t('ilgan', { stem }) : t('popular')

  return (
    <section>
      <h2 className="mb-3 text-[17px] font-extrabold text-c-text">{title}</h2>
      <ul className="-mx-4 flex snap-x snap-mandatory scroll-px-4 gap-3 overflow-x-auto px-4 pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {shelf.productIds.map((id) => {
          const product = getProduct(id)
          return (
            <li key={id} className="w-[44%] max-w-[200px] shrink-0 snap-start">
              <ProductLink product={product} className={PRESS}>
                <PosterCard product={product} />
              </ProductLink>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
