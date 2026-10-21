import { describe, expect, it } from 'vitest'
import { PRODUCTS, CATEGORY_ORDER, getProduct, productsInCategory } from './products'

describe('products', () => {
  it('has unique ids', () => {
    const ids = PRODUCTS.map((p) => p.id)
    expect(new Set(ids).size).toBe(ids.length)
  })
  it('available iff href', () => {
    for (const p of PRODUCTS) expect(p.status === 'available').toBe(p.href !== null)
  })
  it('has keywords in both locales', () => {
    for (const p of PRODUCTS) {
      expect(p.keywords.ko.length).toBeGreaterThan(0)
      expect(p.keywords.en.length).toBeGreaterThan(0)
    }
  })
  it('love category membership', () => {
    const ids = productsInCategory('love').map((p) => p.id)
    for (const id of ['some_heart', 'reunion', 'compatibility', 'guriguri_counsel']) expect(ids).toContain(id)
  })
  it('category order and getProduct', () => {
    expect(CATEGORY_ORDER).toEqual(['fortune', 'love', 'reunion', 'compat', 'career', 'money'])
    expect(getProduct('reunion').status).toBe('coming_soon')
  })
})
