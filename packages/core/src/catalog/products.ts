export type ProductId =
  | 'daily_fortune' | 'guriguri_counsel' | 'saju_report' | 'compatibility'
  | 'question' | 'some_heart' | 'reunion' | 'career_move' | 'money_flow'
export type ProductCategory = 'fortune' | 'love' | 'reunion' | 'compat' | 'career' | 'money'

export const CATEGORY_ORDER: readonly ProductCategory[] = [
  'fortune', 'love', 'reunion', 'compat', 'career', 'money',
]

export interface Product {
  id: ProductId
  categories: ProductCategory[]
  status: 'available' | 'coming_soon'
  /** available only; app path without locale prefix */
  href: string | null
  art: string
  keywords: { ko: string[]; en: string[] }
}

export const PRODUCTS: readonly Product[] = [
  {
    id: 'daily_fortune', categories: ['fortune'], status: 'available', href: '/fortune',
    art: '/mascot/fortune.png',
    keywords: {
      ko: ['오늘의운세', '운세', '일일운세', '오늘운세', '운세스토리', '오늘'],
      en: ['daily fortune', 'fortune', 'today', 'horoscope', 'luck'],
    },
  },
  {
    id: 'guriguri_counsel', categories: ['love', 'career', 'money'], status: 'available', href: '/chat',
    art: '/mascot/thumbsup.png',
    keywords: {
      ko: ['구리구리상담', '구리구리', '상담', '고민', '채팅', '사주상담'],
      en: ['guriguri counsel', 'guriguri', 'counsel', 'counseling', 'chat', 'advice', 'worry'],
    },
  },
  {
    id: 'saju_report', categories: ['fortune'], status: 'available', href: '/report/new',
    art: '/mascot/calendar.png',
    keywords: {
      ko: ['사주리포트', '리포트', '사주풀이', '사주', '신년운세', '올해운세', '평생운세'],
      en: ['saju report', 'report', 'saju reading', 'saju', 'yearly fortune'],
    },
  },
  {
    id: 'compatibility', categories: ['compat', 'love'], status: 'available', href: '/compatibility/new',
    art: '/mascot/love.png',
    keywords: {
      ko: ['궁합', '속궁합', '커플', '연애궁합', '연인', '남친', '여친'],
      en: ['compatibility', 'match', 'couple', 'love match', 'partner'],
    },
  },
  {
    id: 'question', categories: ['fortune'], status: 'available', href: '/question',
    art: '/mascot/cookie.png',
    keywords: {
      ko: ['질문하기', '질문', '한줄질문', '예스노', '타이밍', '결정'],
      en: ['question', 'ask', 'yes or no', 'quick question', 'decision'],
    },
  },
  {
    id: 'some_heart', categories: ['love'], status: 'coming_soon', href: null,
    art: '/mascot/love.png',
    keywords: {
      ko: ['썸', '짝사랑', '속마음', '썸속마음', '그사람마음', '연애', '고백'],
      en: ['some heart', 'crush', 'his feelings', 'her feelings', 'love interest', 'situationship'],
    },
  },
  {
    id: 'reunion', categories: ['reunion', 'love'], status: 'coming_soon', href: null,
    art: '/mascot/love.png',
    keywords: {
      ko: ['재회', '헤어짐', '이별', '전남친', '전여친', '전애인', '다시만날까'],
      en: ['reunion', 'breakup', 'ex', 'get back together', 'ex boyfriend', 'ex girlfriend'],
    },
  },
  {
    id: 'career_move', categories: ['career'], status: 'coming_soon', href: null,
    art: '/mascot/calendar.png',
    keywords: {
      ko: ['이직', '퇴사', '회사', '직장', '취업', '커리어', '승진'],
      en: ['career move', 'career', 'job change', 'quit', 'resign', 'job', 'promotion'],
    },
  },
  {
    id: 'money_flow', categories: ['money'], status: 'coming_soon', href: null,
    art: '/mascot/cookie.png',
    keywords: {
      ko: ['돈', '재물', '월급', '재물운', '금전운', '투자', '재테크'],
      en: ['money flow', 'money', 'wealth', 'salary', 'finance', 'investment'],
    },
  },
]

export function getProduct(id: ProductId): Product {
  const p = PRODUCTS.find((x) => x.id === id)
  if (!p) throw new Error(`Unknown product: ${id}`)
  return p
}

export function productsInCategory(cat: ProductCategory): Product[] {
  return PRODUCTS.filter((p) => p.categories.includes(cat))
}
