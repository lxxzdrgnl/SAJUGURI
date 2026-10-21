import { describe, expect, it } from 'vitest'
import type { DailyStoryResponse } from '@sajuguri/api-client'
import { summarizeStory } from './fortuneSummary'

const base = { date: '2026-10-21', day_ganji: { stem: '갑', branch: '자' }, profile_name: '', scores: {}, keyword: '', record_id: null, rewritten: true }
const story = (cards: unknown[]) => ({ ...base, cards }) as unknown as DailyStoryResponse

describe('summarizeStory', () => {
  it('null이면 안 본 상태', () => {
    expect(summarizeStory(null)).toEqual({ seen: false })
  })
  it('overall 카드의 점수와 헤드라인을 돌려준다', () => {
    const s = story([
      { kind: 'intro', title: 'a', headline: 'x', body: '' },
      { kind: 'overall', title: 'b', score: 72, headline: '말 한마디가 판을 바꾸는 날', body: '' },
    ])
    expect(summarizeStory(s)).toEqual({ seen: true, score: 72, headline: '말 한마디가 판을 바꾸는 날' })
  })
  it('overall 카드가 없으면 안 본 상태', () => {
    expect(summarizeStory(story([{ kind: 'intro', title: 'a', headline: 'x', body: '' }]))).toEqual({ seen: false })
  })
  it('overall에 score가 없으면 안 본 상태', () => {
    expect(summarizeStory(story([{ kind: 'overall', title: 'b', headline: 'h', body: '' }]))).toEqual({ seen: false })
  })
})
