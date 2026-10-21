import { CATEGORY_ORDER, type ProductCategory } from '@sajuguri/core'

/** ?cat= 값이 알려진 상품 카테고리인지 — 아니면 "전체"로 본다 */
export function isCategory(v: unknown): v is ProductCategory {
  return typeof v === 'string' && (CATEGORY_ORDER as readonly string[]).includes(v)
}
