/** globals.css의 테마 대응 오행 변수 키 (--c-oh-*) — 값 원천은 packages/design ohaengByTheme */
const OHAENG_VAR_KEY: Record<string, string> = { 목: 'mok', 화: 'hwa', 토: 'to', 금: 'geum', 수: 'su' }

/** 오행 → CSS 변수 (라이트/다크 자동 전환). style·SVG fill용 — HEX 연산(`${c}1A` 등)에는 쓰지 말 것 */
export function ohaengVar(element: string): string {
  const k = OHAENG_VAR_KEY[element]
  return k ? `var(--c-oh-${k})` : 'var(--c-text)'
}

/** 오행 → 틴트 CSS 변수 (기둥 카드 배경 등) */
export function ohaengTintVar(element: string): string {
  const k = OHAENG_VAR_KEY[element]
  return k ? `var(--c-oh-${k}-tint)` : 'var(--c-surface)'
}
