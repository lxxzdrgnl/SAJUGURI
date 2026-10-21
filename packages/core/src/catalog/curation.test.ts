import { describe, expect, it } from 'vitest'
import { curatedShelf, curatedRanking, SITUATIONS } from './curation'
import { PRODUCTS } from './products'

const ids = new Set<string>(PRODUCTS.map((p) => p.id))

describe('curation', () => {
  it('ilgan shelf', () => {
    const s = curatedShelf('임')
    expect(s.kind).toBe('ilgan')
    expect(s.productIds.length).toBeGreaterThanOrEqual(3)
    expect(s.productIds.length).toBeLessThanOrEqual(4)
  })
  it('popular fallback', () => {
    expect(curatedShelf(null).kind).toBe('popular')
    expect(curatedShelf('X').kind).toBe('popular')
  })
  it('all stems valid with a coming_soon', () => {
    for (const st of '갑을병정무기경신임계') {
      const s = curatedShelf(st)
      expect(s.kind).toBe('ilgan')
      expect(s.productIds.every((i) => ids.has(i))).toBe(true)
      expect(s.productIds.some((i) => PRODUCTS.find((p) => p.id === i)!.status === 'coming_soon')).toBe(true)
    }
    expect(curatedShelf(null).productIds.every((i) => ids.has(i))).toBe(true)
  })
  it('ranking and situations', () => {
    expect(curatedRanking()).toEqual(['daily_fortune', 'compatibility', 'saju_report'])
    expect(SITUATIONS.map((s) => [s.key, s.productId])).toEqual([
      ['some', 'some_heart'], ['breakup', 'reunion'], ['quit', 'career_move'], ['money', 'money_flow'],
    ])
  })
})
