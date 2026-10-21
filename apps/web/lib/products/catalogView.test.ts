import { describe, it, expect } from 'vitest'
import { CATEGORY_ORDER, getProduct, type Product } from '@sajuguri/core'
import { isCategory } from './category'
import { posterTone } from './posterTone'

describe('isCategory', () => {
  it('CATEGORY_ORDER 값은 참', () => {
    for (const c of CATEGORY_ORDER) expect(isCategory(c)).toBe(true)
  })
  it('all·모르는 값·비문자열은 거짓', () => {
    expect(isCategory('all')).toBe(false)
    expect(isCategory('LOVE')).toBe(false)
    expect(isCategory('')).toBe(false)
    expect(isCategory(undefined)).toBe(false)
    expect(isCategory(['love'])).toBe(false)
  })
})

describe('posterTone', () => {
  it('첫 카테고리의 포스터 토큰', () => {
    expect(posterTone(getProduct('daily_fortune'))).toBe('bg-c-poster-butter')
    expect(posterTone(getProduct('reunion'))).toBe('bg-c-poster-lilac')
    expect(posterTone(getProduct('career_move'))).toBe('bg-c-poster-sky')
  })
  it('카테고리가 없거나 모르면 surface-soft로 폴백', () => {
    const base = getProduct('question')
    expect(posterTone({ ...base, categories: [] } as Product)).toBe('bg-c-surface-soft')
    expect(posterTone({ ...base, categories: ['unknown'] } as unknown as Product)).toBe('bg-c-surface-soft')
  })
})
