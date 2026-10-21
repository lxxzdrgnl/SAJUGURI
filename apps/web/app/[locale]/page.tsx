import { getLocale, getTranslations } from 'next-intl/server'
import {
  STEM_HANJA,
  curatedRanking,
  curatedShelf,
  getProduct,
  productsInCategory,
  type ProductId,
} from '@sajuguri/core'
import { listProfiles, type ProfileResponse } from '@sajuguri/api-client'
import { currentUser, serverAuthApi } from '@/lib/serverAuth'
import { buttonClass } from '@/components/ui/Button'
import CategoryTabs from '@/components/home/CategoryTabs'
import HeroCarousel from '@/components/home/HeroCarousel'
import FortuneHeroCard from '@/components/home/FortuneHeroCard'
import CounselCard from '@/components/home/CounselCard'
import SituationGrid from '@/components/home/SituationGrid'
import ProductShelf from '@/components/home/ProductShelf'
import RankList from '@/components/home/RankList'
import ProductGrid from '@/components/home/ProductGrid'
import ProductLink from '@/components/home/ProductLink'
import { posterTone } from '@/lib/products/posterTone'
import { isCategory } from '@/lib/products/category'
import { HomeViewerProvider } from '@/components/home/HomeViewer'

/** 히어로 2~3번째 장 — 오늘의 운세 뒤에 붙는 추천 상품 */
const HERO_PROMOS: ProductId[] = ['saju_report', 'compatibility']

/** 히어로 추천 슬라이드 — 상품 제목·설명·스티커 + 버튼 모양 */
async function PromoSlide({ id }: { id: ProductId }) {
  const product = getProduct(id)
  const tp = await getTranslations('products')
  const t = await getTranslations('home.hero')
  return (
    <ProductLink product={product} className="h-full">
      <span className={`flex h-full min-h-[168px] items-center gap-4 rounded-card p-5 text-c-text ${posterTone(product)}`}>
        <span className="min-w-0 flex-1">
          <span className="block break-keep font-display text-xl font-normal leading-snug">{tp(`${id}.title`)}</span>
          <span className="mt-1.5 line-clamp-2 break-keep text-sm text-c-text-sub">{tp(`${id}.desc`)}</span>
          <span className={`${buttonClass('secondary', 'sm')} mt-3`}>{t('promoCta')}</span>
        </span>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={product.art} alt="" aria-hidden="true" width={96} height={96} className="h-24 w-24 shrink-0 object-contain" />
      </span>
    </ProductLink>
  )
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ cat?: string | string[] }>
}) {
  const rawCat = (await searchParams).cat
  const cat = Array.isArray(rawCat) ? rawCat[0] : rawCat
  const locale = (await getLocale()) === 'en' ? 'en' : 'ko'
  const user = await currentUser()

  // 저장 만세력 — 운세 시트·선반 개인화용 (비로그인·장애 시 빈 배열)
  let profiles: ProfileResponse[] = []
  if (user) {
    try {
      profiles = await listProfiles(await serverAuthApi())
    } catch {
      profiles = []
    }
  }
  const repProfile = profiles.find((p) => p.is_representative) ?? null

  // 흰 바탕 진열대 — 레이아웃 래퍼의 여백까지 덮는다 (가로 폭은 래퍼와 같다)
  const shell = '-mx-4 -mb-8 -mt-2 min-h-[calc(100dvh-3.5rem)] bg-c-bg px-4 pb-10'

  if (isCategory(cat)) {
    return (
      <HomeViewerProvider profiles={profiles} isLoggedIn={!!user}>
        <main className={shell}>
          <CategoryTabs active={cat} />
          <div className="pt-5">
            <ProductGrid products={productsInCategory(cat)} />
          </div>
        </main>
      </HomeViewerProvider>
    )
  }

  const dayStem = repProfile?.day_stem ?? null
  // en 문구엔 한글 천간 대신 한자를 넣는다 (글로서리에 천간 로마자 표기가 없다)
  const stemLabel = dayStem ? (locale === 'en' ? (STEM_HANJA[dayStem] ?? null) : dayStem) : null

  const slides = [
    <FortuneHeroCard key="fortune" profiles={profiles} isLoggedIn={!!user} />,
    ...HERO_PROMOS.map((id) => <PromoSlide key={id} id={id} />),
  ]

  return (
    <HomeViewerProvider profiles={profiles} isLoggedIn={!!user}>
      <main className={shell}>
        <CategoryTabs active="all" />
        <div className="flex flex-col gap-8 pt-5">
          <div className="flex flex-col gap-3">
            <HeroCarousel slides={slides} />
            <CounselCard size="row" profile={repProfile} />
          </div>
          <SituationGrid />
          <ProductShelf shelf={curatedShelf(dayStem)} stem={stemLabel} />
          <RankList ids={curatedRanking()} />
        </div>
      </main>
    </HomeViewerProvider>
  )
}
