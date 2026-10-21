import { describe, it, expect } from 'vitest'
import { ohaengVar, ohaengTintVar } from './ohaeng'

describe('오행 CSS 변수 (테마 대응 — globals.css --c-oh-*)', () => {
  it('5원소 → var(--c-oh-*), 미지정은 본문/표면 폴백', () => {
    expect(ohaengVar('목')).toBe('var(--c-oh-mok)')
    expect(ohaengVar('수')).toBe('var(--c-oh-su)')
    expect(ohaengVar('???')).toBe('var(--c-text)')
    expect(ohaengTintVar('금')).toBe('var(--c-oh-geum-tint)')
    expect(ohaengTintVar('???')).toBe('var(--c-surface)')
  })
})

