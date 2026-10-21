import { describe, expect, it } from 'vitest'
import { ageBand } from './ageBand'

const today = new Date('2026-10-21')
describe('ageBand', () => {
  it('25-29', () => expect(ageBand('2001-08-17', today)).toBe('25-29'))
  it('15-19', () => expect(ageBand('2010-01-01', today)).toBe('15-19'))
  it('birthday not yet reached', () => expect(ageBand('2001-12-01', today)).toBe('20-24'))
  it('future -> null', () => expect(ageBand('2030-01-01', today)).toBeNull())
  it('invalid -> null', () => expect(ageBand('not-a-date', today)).toBeNull())
  it('uses local date parts (birthday just after local midnight)', () =>
    expect(ageBand('2001-08-17', new Date(2026, 7, 17, 0, 30))).toBe('25-29'))
  it('uses local date parts (day before birthday late evening)', () =>
    expect(ageBand('2001-08-17', new Date(2026, 7, 16, 23, 30))).toBe('20-24'))
})
