/**
 * 오행 색상 — 프로젝트 전체 단일 소스
 * ⚠️  main.css :root --el-* 변수와 동일한 hex 값을 유지해야 합니다.
 */
export const EL_HEX: Record<string, string> = {
  '목': '#4a9490',
  '화': '#c04838',
  '토': '#8b5e30',  // 갈색
  '금': '#b89020',  // 황금색
  '수': '#3858b0',  // 남색/인디고
}

/** 오행 → CSS 변수 참조 문자열 (템플릿 인라인 스타일용) */
export function elColor(el: string): string {
  return `var(--el-${el}, #888888)`
}

/**
 * 오행 배경 인라인 스타일 (반투명 배경 + 보더 + 텍스트색)
 * color-mix()로 CSS 변수에서 자동 계산 → main.css 변경만으로 반영
 */
export function elBgStyle(el: string, opacity = 8): string {
  const v = `var(--el-${el}, #888888)`
  return [
    `background: color-mix(in srgb, ${v} ${opacity}%, transparent)`,
    `border-color: color-mix(in srgb, ${v} 30%, transparent)`,
    `color: ${v}`,
  ].join('; ')
}
