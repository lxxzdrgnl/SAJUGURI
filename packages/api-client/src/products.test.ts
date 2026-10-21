import { describe, it, expect, vi } from 'vitest'
import { recordProductView } from './products'
import type { ApiClient } from './client'

describe('recordProductView', () => {
  it('POST /api/products/views', async () => {
    const api = { post: vi.fn().mockResolvedValue(undefined) } as unknown as ApiClient
    const body = { product_id: 'reunion', day_stem: '임', age_band: '25-29', gender: 'male' }
    await recordProductView(api, body)
    expect(api.post).toHaveBeenCalledWith('/api/products/views', body)
  })
})
