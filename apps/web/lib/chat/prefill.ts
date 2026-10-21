import { PRODUCTS } from '@sajuguri/core'

/** 첫 입력 힌트 최대 길이 — URL로 들어온 임의 문자열을 제한한다 */
export const PREFILL_MAX = 500

/** 쿼리 값 하나만 취한다 (?q=a&q=b → a) */
export const firstParam = (v?: string | string[]) => (Array.isArray(v) ? v[0] : v)

/** ?q= 텍스트 정리 — 공백만이면 null, 길면 자른다 */
export function clampPrefill(q?: string | null): string | null {
  const text = q?.trim()
  return text ? text.slice(0, PREFILL_MAX) : null
}

/**
 * 새 상담 첫 입력창 힌트 — ?topic=<ProductId>가 알려진 상품이고 상담 문구가 있으면 그것,
 * 아니면 ?q=<문구>. topic이 우선한다. 자동 전송은 하지 않는다.
 * @param counselPrompt 상품 id → 상담 문구 (메시지에 없으면 null)
 */
export function resolvePrefill(
  topic: string | undefined,
  q: string | undefined,
  counselPrompt: (productId: string) => string | null,
): string | null {
  if (topic && PRODUCTS.some((p) => p.id === topic)) {
    const prompt = counselPrompt(topic)
    if (prompt) return prompt
  }
  return clampPrefill(q)
}
