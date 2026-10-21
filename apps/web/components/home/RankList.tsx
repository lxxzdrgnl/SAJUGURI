import { useTranslations } from 'next-intl'
import { getProduct, type ProductId } from '@sajuguri/core'
import ProductLink from './ProductLink'
import { posterTone } from '@/lib/products/posterTone'

/** 랭킹 리스트 — 번호 · 58px 썸네일 · 제목 · 설명. 큐레이션 동안 제목은 "구리구리 추천". */
export default function RankList({
  ids,
}: {
  ids: ProductId[]
}) {
  const t = useTranslations('home.ranking')
  const tp = useTranslations('products')

  return (
    <section>
      <h2 className="mb-1 text-[17px] font-extrabold text-c-text">{t('title')}</h2>
      <ol className="divide-y divide-c-line">
        {ids.map((id, i) => {
          const product = getProduct(id)
          return (
            <li key={id}>
              <ProductLink product={product} className="transition-opacity active:opacity-60">
                <span className="flex items-center gap-3 py-3">
                  <span className="w-5 shrink-0 text-center font-display text-lg font-normal text-c-text">
                    {i + 1}
                  </span>
                  <span className={`flex h-[58px] w-[58px] shrink-0 items-center justify-center rounded-[16px] ${posterTone(product)}`}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={product.art}
                      alt=""
                      aria-hidden="true"
                      width={44}
                      height={44}
                      loading="lazy"
                      className="h-11 w-11 object-contain"
                    />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-[15px] font-extrabold text-c-text">
                      {tp(`${id}.title`)}
                    </span>
                    <span className="mt-0.5 block truncate text-[13px] text-c-text-sub">{tp(`${id}.desc`)}</span>
                  </span>
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                    className="shrink-0 text-c-text-sub"
                  >
                    <path d="M9 6l6 6-6 6" />
                  </svg>
                </span>
              </ProductLink>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
