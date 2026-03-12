/**
 * 도시 진태양시 보정 유틸리티.
 *
 * 백엔드 GET /api/cities?q=... 호출 → geonamescache + timezonefinder 기반
 * 한국어/영문 통합 검색 지원.
 *
 * 보정 공식: Math.round(longitude × 4) − utcOffsetMinutes
 *   서울: round(126.97 × 4) − 540 = 508 − 540 = −32분
 */

export interface CityOption {
  label: string       // 표시명
  sublabel: string    // 국가·영문명
  longitude: number
  utcOffset: number   // 분 단위 표준시
  isKorea: boolean
  timezone: string
}

/** 진태양시 보정값 계산 (분) */
export function calcSolarCorrection(longitude: number, utcOffsetMinutes: number): number {
  return Math.round(longitude * 4) - utcOffsetMinutes
}

/** 보정값을 사람이 읽기 좋은 문자열로 */
export function formatCorrection(minutes: number): string {
  const sign = minutes >= 0 ? '+' : ''
  return `${sign}${minutes}분`
}

/** 백엔드 API로 도시 검색 (한국어/영문 통합) */
export async function searchCities(query: string): Promise<CityOption[]> {
  const q = query.trim()
  if (!q) return []
  try {
    const res = await fetch(`/api/cities?q=${encodeURIComponent(q)}`)
    if (!res.ok) return []
    const data: Array<{
      label: string; sublabel: string; longitude: number
      utc_offset: number; timezone: string; is_korea: boolean
    }> = await res.json()
    return data.map(d => ({
      label: d.label,
      sublabel: d.sublabel,
      longitude: d.longitude,
      utcOffset: d.utc_offset,
      timezone: d.timezone,
      isKorea: d.is_korea,
    }))
  } catch {
    return []
  }
}

/** 서울 기본 보정 (-32분) */
export const SEOUL_CORRECTION = -32
