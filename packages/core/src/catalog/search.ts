import { PRODUCTS, type Product } from './products'

const norm = (s: string) => s.trim().toLowerCase().replace(/\s+/g, '')

export function searchProducts(query: string, locale: 'ko' | 'en'): Product[] {
  const q = norm(query)
  if (!q) return []
  const exact: Product[] = []
  const partial: Product[] = []
  for (const p of PRODUCTS) {
    const kws = p.keywords[locale].map(norm)
    if (kws.includes(q)) exact.push(p)
    else if (kws.some((k) => k.includes(q) || q.includes(k))) partial.push(p)
  }
  return [...exact, ...partial]
}
