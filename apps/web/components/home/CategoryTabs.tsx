import { useTranslations } from 'next-intl'
import { CATEGORY_ORDER, type ProductCategory } from '@sajuguri/core'
import { Link } from '@/i18n/navigation'

/** 홈 카테고리 탭 — 전체(쿼리 없음) + 카테고리별 ?cat=. 탭 줄만 가로 스크롤된다. */
export default function CategoryTabs({ active }: { active: ProductCategory | 'all' }) {
  const t = useTranslations('categories')
  const tHome = useTranslations('home')
  const tabs: (ProductCategory | 'all')[] = ['all', ...CATEGORY_ORDER]

  return (
    <nav aria-label={tHome('tabsLabel')} className="-mx-4 border-b border-c-line">
      <ul className="flex gap-5 overflow-x-auto px-4 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {tabs.map((key) => {
          const isActive = key === active
          return (
            <li key={key} className="shrink-0">
              <Link
                href={key === 'all' ? '/' : { pathname: '/', query: { cat: key } }}
                scroll={false}
                aria-current={isActive ? 'page' : undefined}
                className={`relative flex h-11 items-center whitespace-nowrap text-[15px] transition-colors ${
                  isActive ? 'font-extrabold text-c-text' : 'font-semibold text-c-text-sub hover:text-c-text'
                }`}
              >
                {t(key)}
                {isActive && (
                  <span aria-hidden="true" className="absolute inset-x-0 -bottom-px h-[3px] rounded-pill bg-c-accent" />
                )}
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
