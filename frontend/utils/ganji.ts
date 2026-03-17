/**
 * 명리학 간지(干支) 상수 및 헬퍼 — 프로젝트 전체 단일 소스
 */

export const STEMS = ['갑','을','병','정','무','기','경','신','임','계'] as const
export const BRANCHES = ['자','축','인','묘','진','사','오','미','신','유','술','해'] as const

export const STEM_HANJA: Record<string, string> = {
  '갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊',
  '기':'己','경':'庚','신':'辛','임':'壬','계':'癸',
}
export const BRANCH_HANJA: Record<string, string> = {
  '자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳',
  '오':'午','미':'未','신':'申','유':'酉','술':'戌','해':'亥',
}
export const STEM_COLOR: Record<string, string> = {
  '갑':'청','을':'청','병':'붉은','정':'붉은','무':'황금',
  '기':'황금','경':'흰','신':'흰','임':'검은','계':'검은',
}

/** 오행 색이름 텍스트 자체의 표시 색상 (한자 색상과 구분) */
export const STEM_COLOR_CSS: Record<string, string> = {
  '청':   'var(--el-목)',
  '붉은': 'var(--el-화)',
  '황금': 'var(--el-토)',
  '흰':   '#c8c8c8',
  '검은': 'var(--text-secondary)',
}

/** 색이름 레이블을 실제 시각 색상으로 변환 */
export function stemLabelColor(colorLabel: string): string {
  return STEM_COLOR_CSS[colorLabel] ?? 'var(--text-secondary)'
}
export const STEM_ELEMENT: Record<string, string> = {
  '갑':'목','을':'목','병':'화','정':'화','무':'토',
  '기':'토','경':'금','신':'금','임':'수','계':'수',
}
export const BRANCH_ELEMENT: Record<string, string> = {
  '자':'수','축':'토','인':'목','묘':'목','진':'토','사':'화',
  '오':'화','미':'토','신':'금','유':'금','술':'토','해':'수',
}
export const BRANCH_ANIMAL: Record<string, string> = {
  '자':'쥐','축':'소','인':'호랑이','묘':'토끼',
  '진':'용','사':'뱀','오':'말','미':'양',
  '신':'원숭이','유':'닭','술':'개','해':'돼지',
}

export const TEN_GOD_ELEMENT: Record<string, string> = {
  '비견':'목','겁재':'목','식신':'화','상관':'화',
  '편재':'토','정재':'토','편관':'금','정관':'금',
  '편인':'수','정인':'수',
}

export const KOREAN_DAYS = ['일','월','화','수','목','금','토'] as const
export const KOREAN_MONTHS = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'] as const

/** 기준일 1900-01-01 = 갑술일(stemIdx=0, branchIdx=10) 기준 오늘 일주 계산 */
export function calcTodayIlju(): { stem: string; branch: string } {
  const base = new Date(1900, 0, 1)
  const today = new Date()
  const days = Math.floor((today.getTime() - base.getTime()) / 86400000)
  const stemIdx = ((days % 10) + 10) % 10
  const branchIdx = ((days + 10) % 12 + 12) % 12
  return { stem: STEMS[stemIdx], branch: BRANCHES[branchIdx] }
}

/** "2026년 3월 16일 (일)" 형식 */
export function formatTodayLabel(): string {
  const d = new Date()
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일 (${KOREAN_DAYS[d.getDay()]})`
}

/** 일주 한자 표기: 甲子 */
export function formatIljuHanja(stem: string | null | undefined, branch: string | null | undefined): string {
  if (!stem || !branch) return ''
  return `${STEM_HANJA[stem] ?? stem}${BRANCH_HANJA[branch] ?? branch}`
}

/** 일주 한글 레이블: "흰 말" */
export function formatIljuLabel(stem: string | null | undefined, branch: string | null | undefined): string {
  if (!stem || !branch) return ''
  return `${STEM_COLOR[stem] ?? stem} ${BRANCH_ANIMAL[branch] ?? branch}`
}

/** 일주/오행 색상 CSS 변수 */
export function iljuColor(element: string | null | undefined): string {
  if (!element) return 'var(--text-secondary)'
  if (element === '수') return '#888'
  return `var(--el-${element})`
}

/** 오행 → 배경 스와치 CSS 변수 맵 (도넛 차트·카드 색상 등에 사용) */
export const EL_SWATCH: Record<string, string> = {
  '목': 'var(--el-목)',
  '화': 'var(--el-화)',
  '토': 'var(--el-토)',
  '금': 'var(--el-금)',
  '수': 'var(--el-수)',
}

/** 운세 점수(0-100) → CSS 색상 변수 */
export function scoreColor(score: number): string {
  if (score >= 80) return 'var(--color-good)'
  if (score >= 60) return 'var(--accent)'
  if (score >= 45) return '#c07818'
  return 'var(--color-bad)'
}
