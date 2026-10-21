import { describe, it, expect, vi } from 'vitest'
import type { ProfileResponse } from '@sajuguri/api-client'
import { recordProductView } from '@sajuguri/api-client'
import { buildViewBody, trackProductView } from './track'

vi.mock('@sajuguri/api-client', async (orig) => ({
  ...(await orig<typeof import('@sajuguri/api-client')>()),
  recordProductView: vi.fn(),
}))
vi.mock('../api', () => ({ api: {} }))

const today = new Date('2026-10-21T00:00:00Z')

describe('buildViewBody', () => {
  it('프로필 없으면 product_id만', () => {
    expect(buildViewBody('reunion', null, today)).toEqual({ product_id: 'reunion' })
  })
  it('대표 프로필이면 day_stem·age_band·gender 포함', () => {
    const profile = { birth_date: '2001-08-17', day_stem: '임', gender: 'male' } as ProfileResponse
    expect(buildViewBody('reunion', profile, today)).toEqual({
      product_id: 'reunion', day_stem: '임', age_band: '25-29', gender: 'male',
    })
  })
})

describe('trackProductView', () => {
  it('fetch가 reject돼도 throw/unhandled rejection 없음', async () => {
    vi.mocked(recordProductView).mockRejectedValueOnce(new Error('network down'))
    expect(() => trackProductView('reunion', null)).not.toThrow()
    await new Promise((r) => setTimeout(r, 0))
    expect(recordProductView).toHaveBeenCalledTimes(1)
  })
})
