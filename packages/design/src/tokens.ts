/** 사주구리 디자인 토큰 — 단일 진실 원천: docs/design.md */

export const colors = {
  bgBase: '#EEF1F6',
  ink: '#14161C',
  yellow: '#FFD900',
  yellowTint: '#FFF3B0',
  amber: '#FFB200',
  orange: '#FF6B00',
  orangeTint: '#FFE1CC',
  teal: '#00C2B8',
  tealDeep: '#00857D',
  tealTint: '#D7F7F4',
  surface: '#FFFFFF',
  borderSoft: '#C8D0DE',
  textSub: '#6B7488',
  sky: '#4DA8E8',
  skyTint: '#DCEFFB',
} as const

/** 오행 5색 — 전통 5색 대체, 팔레트 파생 (design.md §2.2) */
export const ohaeng = {
  목: '#00A86B',
  화: '#FF6B00',
  토: '#D9A400',
  금: '#7D7A70',
  수: '#0090A8',
} as const

/** 기둥 카드 배경 틴트 */
export const ohaengTint = {
  목: '#E9FAF1',
  화: '#FFF1E8',
  토: '#FBF3D9',
  금: '#F4F2EC',
  수: '#E8F7FA',
} as const

/** 스토리(오늘의 운세) 전용 */
export const story = {
  gradientFrom: '#00857D',
  gradientTo: '#04332F',
  score: '#FF8A2E',
  progressFill: '#FFD900',
} as const

export const radius = {
  card: '10px',
  button: '8px',
  chip: '8px',
  pill: '999px',
  sheet: '16px',
} as const

export const shadow = {
  brutal: '4px 4px 0 var(--ink)',
  brutalSm: '2px 2px 0 var(--ink)',
  brutalOrange: '4px 4px 0 var(--orange)',
} as const

/** Y2K 재료 — 크롬(금속 다단)·홀로그램(무지개 conic)·글로스(광택 inset) */
export const y2k = {
  chrome:
    'linear-gradient(158deg,#FDFEFF 0%,#CBD4E2 16%,#8E9BB0 32%,#EAEFF7 46%,' +
    '#6E7C93 60%,#AEBACB 74%,#F4F8FD 100%)',
  holo:
    'conic-gradient(from 210deg,#6EE7FF,#C6F432,#FFD900,#FF5FD2,#A78BFA,#6EE7FF)',
  gloss:
    'inset 0 1.5px 0 rgba(255,255,255,.9), inset 0 -3px 8px rgba(20,22,28,.10)',
  specular:
    'linear-gradient(102deg,transparent 34%,rgba(255,255,255,.85) 46%,transparent 56%)',
} as const

/** 차트 점수 색 의미: 피크=orange, 중간=yellow, 저점=tealTint */
export const chartScore = {
  peak: colors.orange,
  mid: colors.yellow,
  low: colors.tealTint,
} as const

export const layout = {
  maxWidth: '640px',
} as const

/** colors만 CSS 변수 :root 블록으로 변환 (radius·shadow 등은 대상 아님) — apps/web globals.css에서 사용 */
export function toCssVariables(): string {
  const entries: string[] = []
  for (const [k, v] of Object.entries(colors)) {
    entries.push(`--${k.replace(/[A-Z]/g, (m) => '-' + m.toLowerCase())}: ${v};`)
  }
  return `:root {\n  ${entries.join('\n  ')}\n}`
}

// ── 의미 기반 색 토큰 (라이트·다크) ────────────────────────────
export type ThemeName = 'light' | 'dark'

export interface SemanticColors {
  bg: string
  surface: string
  surfaceSoft: string
  line: string
  text: string
  textSub: string
  accent: string
  onAccent: string
  danger: string
  counselBg: string
  counselFg: string
}

export const semantic: Record<ThemeName, SemanticColors> = {
  light: {
    bg: '#FFFFFF',
    surface: '#FFFFFF',
    surfaceSoft: '#FAF6EC',
    line: '#E7E2D6',
    text: '#14161C',
    textSub: '#5B606B',
    accent: '#FFD900',
    onAccent: '#14161C',
    danger: '#D92D20',
    counselBg: '#04332F',
    counselFg: '#E9F4F1',
  },
  dark: {
    bg: '#121212',
    surface: '#1A1A1A',
    surfaceSoft: '#232323',
    line: '#333333',
    text: '#F5F5F5',
    textSub: '#A8ADB7',
    accent: '#FFD900',
    onAccent: '#14161C',
    danger: '#FF6B5E',
    counselBg: '#04332F',
    counselFg: '#E9F4F1',
  },
}

type OhaengKey = '목' | '화' | '토' | '금' | '수'

export const ohaengByTheme: Record<ThemeName, Record<OhaengKey, string>> = {
  light: { 목: '#008A57', 화: '#E05A00', 토: '#A67C00', 금: '#6B7280', 수: '#2B7FD1' },
  dark: { 목: '#2FD28F', 화: '#FF8A3D', 토: '#E5B820', 금: '#B6BCC8', 수: '#5BB0F2' },
}

export const ohaengTintByTheme: Record<ThemeName, Record<OhaengKey, string>> = {
  light: { 목: '#E9FAF1', 화: '#FFEEDD', 토: '#FFF6D1', 금: '#EEF0F3', 수: '#DCEFFB' },
  dark: { 목: '#12261D', 화: '#2B1B10', 토: '#2A2410', 금: '#222428', 수: '#12212E' },
}

/** 포스터 카드 배경 톤 — 홈 진열대 카테고리별 파스텔. apps/web globals.css --c-poster-* 가 미러한다. */
export type PosterTone = 'butter' | 'rose' | 'lilac' | 'peach' | 'sky' | 'mint'

export const posterByTheme: Record<ThemeName, Record<PosterTone, string>> = {
  light: {
    butter: '#FFF3C4',
    rose: '#FDE4EA',
    lilac: '#ECE7FA',
    peach: '#FFE8D9',
    sky: '#E2EEFB',
    mint: '#DDF3EA',
  },
  dark: {
    butter: '#3A3217',
    rose: '#3A2129',
    lilac: '#2A2540',
    peach: '#3B281D',
    sky: '#182A3B',
    mint: '#17332A',
  },
}
