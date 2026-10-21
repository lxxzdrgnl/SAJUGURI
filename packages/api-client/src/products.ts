import type { ApiClient } from './client'

// ── 상품 열람 기록 (백엔드 POST /api/products/views → 204) ──────────────────

export interface ProductViewBody {
  product_id: string
  day_stem?: string | null
  age_band?: string | null
  gender?: string | null
}

/** POST /api/products/views — 상품 열람 1건 기록. */
export async function recordProductView(api: ApiClient, body: ProductViewBody): Promise<void> {
  await api.post<unknown>('/api/products/views', body)
}
