import { describe, it, expect } from 'vitest'
import { ohaengColor, ohaengTintColor, ohaengVar, ohaengTintVar } from './ohaeng'

describe('오행 CSS 변수 (테마 대응 — globals.css --c-oh-*)', () => {
  it('5원소 → var(--c-oh-*), 미지정은 본문/표면 폴백', () => {
    expect(ohaengVar('목')).toBe('var(--c-oh-mok)')
    expect(ohaengVar('수')).toBe('var(--c-oh-su)')
    expect(ohaengVar('???')).toBe('var(--c-text)')
    expect(ohaengTintVar('금')).toBe('var(--c-oh-geum-tint)')
    expect(ohaengTintVar('???')).toBe('var(--c-surface)')
  })
})

describe('오행 색 매핑 (엔진 한글 오행명 → 토큰)', () => {
  it('5원소 + 미지정 폴백', () => {
    expect(ohaengColor('목')).toBe('#00A86B')
    expect(ohaengColor('수')).toBe('#0090A8')
    expect(ohaengColor('???')).toBe('#1A1A1A')      // 폴백 = 잉크
    expect(ohaengTintColor('화')).toBe('#FFF1E8')
    expect(ohaengTintColor('???')).toBe('#FFFFFF')  // 폴백 = surface
  })
})
