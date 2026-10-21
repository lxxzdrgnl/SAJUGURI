import { recordProductView, type ProductViewBody, type ProfileResponse } from '@sajuguri/api-client'
import { ageBand, type ProductId } from '@sajuguri/core'
import { api } from '../api'

/** 열람 기록 본문 구성 — 프로필이 있으면 일간·연령대·성별을 함께 보낸다. */
export function buildViewBody(
  productId: ProductId,
  profile: ProfileResponse | null,
  today: Date,
): ProductViewBody {
  const body: ProductViewBody = { product_id: productId }
  if (!profile) return body
  if (profile.day_stem) body.day_stem = profile.day_stem
  const band = ageBand(profile.birth_date, today)
  if (band) body.age_band = band
  if (profile.gender) body.gender = profile.gender
  return body
}

/** 상품 열람 기록 (fire-and-forget) — 실패해도 호출자에게 영향 없음. */
export function trackProductView(productId: ProductId, profile: ProfileResponse | null): void {
  try {
    recordProductView(api, buildViewBody(productId, profile, new Date())).catch(() => {})
  } catch {
    // 기록 실패는 무시
  }
}
