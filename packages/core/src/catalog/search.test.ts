import { describe, expect, it } from 'vitest'
import { searchProducts } from './search'

describe('searchProducts', () => {
  it('finds reunion by 재회', () => expect(searchProducts('재회', 'ko')[0].id).toBe('reunion'))
  it('normalizes whitespace', () =>
    expect(searchProducts('  이 직 ', 'ko').map((p) => p.id)).toContain('career_move'))
  it('ignores case', () => expect(searchProducts('REUNION', 'en')[0].id).toBe('reunion'))
  it('empty -> []', () => expect(searchProducts('', 'ko')).toEqual([]))
  it('no match -> []', () => expect(searchProducts('ㅋㅋㅋ없는말', 'ko')).toEqual([]))
})
