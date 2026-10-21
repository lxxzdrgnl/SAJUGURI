import { describe, it, expect } from 'vitest'
import type { ProfileResponse } from '@sajuguri/api-client'
import { buildViewBody } from './track'

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
