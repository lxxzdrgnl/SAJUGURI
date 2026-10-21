import { useTranslations } from 'next-intl'
import { SITUATIONS, getProduct } from '@sajuguri/core'
import type { ProfileResponse } from '@sajuguri/api-client'
import ProductLink from './ProductLink'
import { PRESS } from './cardStyles'

/** "지금 내 상황은?" 2×2 — 각 칸은 해당 테마 상품으로 이어진다. */
export default function SituationGrid({ profile = null }: { profile?: ProfileResponse | null }) {
  const t = useTranslations('home.situation')

  return (
    <section>
      <h2 className="mb-3 text-[17px] font-extrabold text-c-text">{t('title')}</h2>
      <ul className="grid grid-cols-2 gap-3">
        {SITUATIONS.map(({ key, productId }) => {
          const product = getProduct(productId)
          return (
            <li key={key}>
              <ProductLink product={product} profile={profile} className={`h-full ${PRESS}`}>
                <span className="flex h-full min-h-[112px] flex-col rounded-card border border-c-line bg-c-surface p-4">
                  <span className="block break-keep text-[15px] font-extrabold leading-snug text-c-text">
                    {t(`${key}.title`)}
                  </span>
                  <span className="mt-1 block break-keep text-[13px] leading-snug text-c-text-sub">
                    {t(`${key}.desc`)}
                  </span>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={product.art}
                    alt=""
                    aria-hidden="true"
                    width={40}
                    height={40}
                    loading="lazy"
                    className="pointer-events-none mt-auto h-10 w-10 self-end object-contain pt-1"
                  />
                </span>
              </ProductLink>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
