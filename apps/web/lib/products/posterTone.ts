import type { Product, ProductCategory } from '@sajuguri/core'

/** 카테고리 → 포스터 배경 토큰 (globals.css --c-poster-*). 상품은 첫 카테고리를 따른다. */
const CATEGORY_TONE: Record<ProductCategory, string> = {
  fortune: 'bg-c-poster-butter',
  love: 'bg-c-poster-rose',
  reunion: 'bg-c-poster-lilac',
  compat: 'bg-c-poster-peach',
  career: 'bg-c-poster-sky',
  money: 'bg-c-poster-mint',
}

export function posterTone(product: Product): string {
  return CATEGORY_TONE[product.categories[0]] ?? 'bg-c-surface-soft'
}
