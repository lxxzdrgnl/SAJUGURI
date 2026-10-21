import { PRODUCTS, type Product } from './products'

const norm = (s: string) => s.trim().toLowerCase().replace(/\s+/g, '')

const SHORT_KEYWORD_MAX = 2

/** 질의가 키워드를 포함하는지 — 짧은 키워드(≤2자)는 토큰 일치/토큰 접두만 인정해 'next'⊃'ex' 같은 오탐을 막는다. */
function queryContainsKeyword(q: string, tokens: string[], k: string): boolean {
  if (!k) return false
  if (k.length > SHORT_KEYWORD_MAX) return q.includes(k)
  return tokens.some((t) => t === k || t.startsWith(k))
}

export function searchProducts(query: string, locale: 'ko' | 'en'): Product[] {
  const q = norm(query)
  if (!q) return []
  const tokens = query.trim().toLowerCase().split(/\s+/).filter(Boolean)
  const exact: Product[] = []
  const partial: Product[] = []
  for (const p of PRODUCTS) {
    const kws = p.keywords[locale].map(norm)
    if (kws.includes(q)) exact.push(p)
    else if (kws.some((k) => k.includes(q) || queryContainsKeyword(q, tokens, k))) partial.push(p)
  }
  return [...exact, ...partial]
}
