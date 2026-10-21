/**
 * 명리 용어 표시 라벨 — 데이터(한글)를 messages `manse.terms`로 렌더 시점에 매핑한다.
 * 영문 표기는 backend/llm/prompts/glossary.py 기준(좁은 칩에선 첫 단어만).
 * 글로서리에 없는 용어(신강·식상·백호대살 등)는 번역하지 않고 원문(한글) 그대로 둔다.
 */
export interface TermT {
  (key: string, values?: Record<string, string>): string
  has(key: string): boolean
}

/** 오행·십성 등 단순 용어: messages에 있으면 번역, 없으면 원문 */
export function termLabel(t: TermT, ko: string | null | undefined): string {
  if (!ko) return ''
  return t.has(`plain.${ko}`) ? t(`plain.${ko}`) : ko
}

/** 격국명 — '비견격' → "Bigyeon Gyeokguk". 앞 용어가 글로서리에 없으면 원문 유지 */
export function gyeokgukLabel(t: TermT, ko: string | null | undefined): string {
  if (!ko) return ''
  const m = ko.match(/^(.+)격$/)
  if (m && t.has(`plain.${m[1]}`)) return t('gyeokgukOf', { name: t(`plain.${m[1]}`) })
  return ko
}

/** 신살명 — '화개살'/'화개' 둘 다 허용(접미 '살' 제거 후 조회). 없는 신살은 원문 */
export function sinSalLabel(t: TermT, ko: string | null | undefined): string {
  if (!ko) return ''
  if (t.has(`sinsal.${ko}`)) return t(`sinsal.${ko}`)
  const base = ko.replace(/살$/, '')
  return t.has(`sinsal.${base}`) ? t(`sinsal.${base}`) : ko
}
