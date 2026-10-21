import { describe, expect, it } from 'vitest'
import { searchProducts } from './search'

describe('searchProducts', () => {
  it('finds reunion by 재회', () => expect(searchProducts('재회', 'ko')[0].id).toBe('reunion'))
  it('normalizes whitespace', () =>
    expect(searchProducts('  이 직 ', 'ko').map((p) => p.id)).toContain('career_move'))
  it('ignores case', () => expect(searchProducts('REUNION', 'en')[0].id).toBe('reunion'))
  it('empty -> []', () => expect(searchProducts('', 'ko')).toEqual([]))
  it('no match -> []', () => expect(searchProducts('ㅋㅋㅋ없는말', 'ko')).toEqual([]))
  it('short keyword does not match inside a longer word (next !~ ex)', () =>
    expect(searchProducts('next', 'en').map((p) => p.id)).not.toContain('reunion'))
  it('short keyword matches as its own token', () =>
    expect(searchProducts('my ex', 'en').map((p) => p.id)).toContain('reunion'))
  it('short ko keyword matches as its own word', () =>
    expect(searchProducts('내 썸 어때', 'ko').map((p) => p.id)).toContain('some_heart'))
  it('short ko keyword with particle (prefix of token) matches', () =>
    expect(searchProducts('썸이 궁금', 'ko').map((p) => p.id)).toContain('some_heart'))
  it('short ko keyword not matched mid-word', () =>
    expect(searchProducts('맛썸맛', 'ko').map((p) => p.id)).not.toContain('some_heart'))
})
