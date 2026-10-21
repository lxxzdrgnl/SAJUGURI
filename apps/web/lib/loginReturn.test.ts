import { beforeEach, describe, expect, it } from 'vitest'
import { consumeReturnTo, saveReturnTo } from './loginReturn'

const store = new Map<string, string>()
beforeEach(() => {
  store.clear()
  ;(globalThis as { sessionStorage?: unknown }).sessionStorage = {
    getItem: (k: string) => store.get(k) ?? null,
    setItem: (k: string, v: string) => void store.set(k, v),
    removeItem: (k: string) => void store.delete(k),
  }
})

describe('loginReturn', () => {
  it('쿼리 포함 일반 경로는 통과', () => {
    saveReturnTo('/chat?topic=love')
    expect(consumeReturnTo()).toBe('/chat?topic=love')
    saveReturnTo('/en/chat?topic=love')
    expect(consumeReturnTo()).toBe('/en/chat?topic=love')
  })
  it.each(['//evil.com', 'https://x', '/\\evil', '', 'javascript:alert(1)'])('거부: %s', (p) => {
    saveReturnTo(p)
    expect(consumeReturnTo()).toBeNull()
  })
  it('두 번째 소비는 null', () => {
    saveReturnTo('/my')
    expect(consumeReturnTo()).toBe('/my')
    expect(consumeReturnTo()).toBeNull()
  })
})
