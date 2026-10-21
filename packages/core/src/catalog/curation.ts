import type { ProductId } from './products'

export type Element = '목' | '화' | '토' | '금' | '수'
export interface Shelf {
  kind: 'ilgan' | 'popular'
  productIds: ProductId[]
}

const STEM_ELEMENT: Record<string, Element> = {
  갑: '목', 을: '목', 병: '화', 정: '화', 무: '토', 기: '토',
  경: '금', 신: '금', 임: '수', 계: '수',
}

const ELEMENT_SHELF: Record<Element, ProductId[]> = {
  목: ['daily_fortune', 'career_move', 'saju_report'],
  화: ['daily_fortune', 'some_heart', 'compatibility'],
  토: ['daily_fortune', 'money_flow', 'guriguri_counsel'],
  금: ['daily_fortune', 'career_move', 'money_flow', 'saju_report'],
  수: ['daily_fortune', 'reunion', 'compatibility'],
}

const POPULAR: ProductId[] = ['daily_fortune', 'compatibility', 'saju_report', 'reunion']

export function curatedShelf(dayStem: string | null): Shelf {
  const el = dayStem ? STEM_ELEMENT[dayStem] : undefined
  if (!el) return { kind: 'popular', productIds: [...POPULAR] }
  return { kind: 'ilgan', productIds: [...ELEMENT_SHELF[el]] }
}

export function curatedRanking(): ProductId[] {
  return ['daily_fortune', 'compatibility', 'saju_report']
}

export const SITUATIONS: readonly { key: 'some' | 'breakup' | 'quit' | 'money'; productId: ProductId }[] = [
  { key: 'some', productId: 'some_heart' },
  { key: 'breakup', productId: 'reunion' },
  { key: 'quit', productId: 'career_move' },
  { key: 'money', productId: 'money_flow' },
]
