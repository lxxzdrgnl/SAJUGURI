import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { parseThemePref, THEME_COOKIE } from './theme'

describe('parseThemePref', () => {
  it('알려진 값은 그대로', () => {
    expect(parseThemePref('dark')).toBe('dark')
    expect(parseThemePref('light')).toBe('light')
    expect(parseThemePref('system')).toBe('system')
  })
  it('없거나 알 수 없는 값은 system', () => {
    expect(parseThemePref(undefined)).toBe('system')
    expect(parseThemePref('blue')).toBe('system')
    expect(parseThemePref('')).toBe('system')
  })
  it('쿠키 이름은 theme', () => {
    expect(THEME_COOKIE).toBe('theme')
  })
})

/** 정규식에 걸린 블록 본문들에서 --c-* 선언을 모은다 */
function collect(css: string, block: RegExp): Map<string, string> {
  const out = new Map<string, string>()
  for (const m of css.matchAll(block)) {
    for (const d of m[1].matchAll(/(--c-[\w-]+)\s*:\s*([^;]+);/g)) out.set(d[1], d[2].trim())
  }
  return out
}

describe('globals.css 다크 블록 동기화', () => {
  const css = readFileSync(join(__dirname, '../app/globals.css'), 'utf8')
  const forced = collect(css, /^:root\[data-theme="dark"\]\s*\{([^}]*)\}/gm)
  const media = css.match(
    /@media \(prefers-color-scheme: dark\)\s*\{\s*:root:not\(\[data-theme="light"\]\)\s*\{([^}]*)\}/,
  )

  it('강제 다크와 시스템 다크가 같은 --c-* 값을 정의한다', () => {
    expect(media).not.toBeNull()
    const system = collect(media![0], /:root:not\(\[data-theme="light"\]\)\s*\{([^}]*)\}/g)
    expect(forced.size).toBeGreaterThan(20)
    expect(Object.fromEntries(system)).toEqual(Object.fromEntries(forced))
  })

  it('라이트의 --c-* 리터럴 토큰은 모두 다크 값이 있다', () => {
    const light = collect(css, /^:root\s*\{([^}]*)\}/gm)
    for (const [k, v] of light) {
      if (v.startsWith('var(')) continue // 별칭은 원본을 따라간다
      expect(forced.has(k), k).toBe(true)
    }
  })
})
