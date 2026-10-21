import { describe, it, expect } from 'vitest'
import { PREFILL_MAX, clampPrefill, firstParam, resolvePrefill } from './prefill'

const prompts: Record<string, string> = { reunion: '헤어진 사람이랑 다시 만날 수 있을지 궁금해' }
const lookup = (id: string) => prompts[id] ?? null

describe('resolvePrefill', () => {
  it('알려진 topic은 상담 문구', () => {
    expect(resolvePrefill('reunion', undefined, lookup)).toBe(prompts.reunion)
  })
  it('모르는 topic은 무시하고 lookup도 부르지 않는다', () => {
    let called = false
    const spy = (id: string) => { called = true; return lookup(id) }
    expect(resolvePrefill('nope', undefined, spy)).toBeNull()
    expect(called).toBe(false)
  })
  it('상담 문구가 없는 상품 topic이면 q로 넘어간다', () => {
    expect(resolvePrefill('saju_report', '내 사주 궁금해', lookup)).toBe('내 사주 궁금해')
  })
  it('topic이 q보다 우선', () => {
    expect(resolvePrefill('reunion', '다른 말', lookup)).toBe(prompts.reunion)
  })
  it('q는 다듬고 500자로 자른다', () => {
    expect(resolvePrefill(undefined, '  안녕  ', lookup)).toBe('안녕')
    expect(resolvePrefill(undefined, 'a'.repeat(PREFILL_MAX + 50), lookup)).toHaveLength(PREFILL_MAX)
    expect(PREFILL_MAX).toBe(500)
  })
  it('둘 다 없거나 공백이면 null', () => {
    expect(resolvePrefill(undefined, undefined, lookup)).toBeNull()
    expect(resolvePrefill(undefined, '   ', lookup)).toBeNull()
  })
})

describe('clampPrefill / firstParam', () => {
  it('null 입력', () => expect(clampPrefill(null)).toBeNull())
  it('배열이면 첫 값', () => {
    expect(firstParam(['a', 'b'])).toBe('a')
    expect(firstParam('x')).toBe('x')
    expect(firstParam(undefined)).toBeUndefined()
  })
})
