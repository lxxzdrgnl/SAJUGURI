import type { DailyStoryResponse } from '@sajuguri/api-client'

export type FortuneSummary = { seen: false } | { seen: true; score: number; headline: string }

/** 캐시된 오늘의 운세에서 홈 카드용 요약(총운 점수·헤드라인)을 뽑는다. */
export function summarizeStory(story: DailyStoryResponse | null): FortuneSummary {
  const overall = story?.cards.find((c) => c.kind === 'overall')
  if (!overall || typeof overall.score !== 'number') return { seen: false }
  return { seen: true, score: overall.score, headline: overall.headline }
}

/** 운세 페이지가 캐시 저장에 쓰는 것과 같은 사용자 로컬 날짜 (YYYY-MM-DD). */
export function todayLocal(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
