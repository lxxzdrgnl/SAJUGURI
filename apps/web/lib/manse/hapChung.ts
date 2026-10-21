import type { SajuCalcResponse } from '@sajuguri/api-client'

/** 합충 분석 로직 — 레거시 HapChungPanel.vue 가공 로직 보존 (branch_relations·gong_mang 해석) */

export type PillarKey = 'year' | 'month' | 'day' | 'hour'
export const PKEYS: PillarKey[] = ['year', 'month', 'day', 'hour']

export type TabKey =
  | 'gung_seong' | 'cheon_gan_hap' | 'yuk_hap' | 'sam_hap' | 'bang_hap'
  | 'cheon_gan_chung' | 'chung' | 'gong_mang' | 'sam_hyeong' | 'pa' | 'yuk_hae' | 'won_jin'

export const ALL_TABS: TabKey[] = [
  'gung_seong', 'cheon_gan_hap', 'yuk_hap', 'sam_hap', 'bang_hap', 'cheon_gan_chung',
  'chung', 'gong_mang', 'sam_hyeong', 'pa', 'yuk_hae', 'won_jin',
]

const SAM_HYEONG: Record<string, string[]> = {
  인사신형: ['인', '사', '신'],
  축술미형: ['축', '술', '미'],
  자형: ['자'],
  오형: ['오'],
}

/** 관계 종류 — 문장은 UI(next-intl)에서 kind별 메시지로 조립 */
export type EntryKind =
  | 'stemHap' | 'stemChung' | 'yukHap' | 'samHap' | 'bangHap'
  | 'chung' | 'gongMang' | 'samHyeong' | 'pa' | 'yukHae' | 'wonJin'

export interface Entry {
  kind: EntryKind
  /** 관계를 이루는 글자 (쌍이면 2개, 이름형이면 [name]) */
  chars: string[]
  /** 문장 앞 "(연주-월주)" 표기에 쓰는 기둥 (없으면 빈 배열) */
  descPillars: PillarKey[]
  /** 공망 엔트리 전용 */
  pillar?: PillarKey
  vacant?: string[]
  stems: PillarKey[]
  branches: PillarKey[]
  resultEl?: string
  broken?: boolean
}

interface PillarLike { stem: string; branch: string }

function pillarOf(saju: SajuCalcResponse, p: PillarKey): PillarLike | null {
  return (saju[`${p}_pillar`] as PillarLike | null) ?? null
}

export function activePillars(saju: SajuCalcResponse): PillarKey[] {
  return PKEYS.filter((p) => pillarOf(saju, p) !== null)
}

function findBranch(saju: SajuCalcResponse, b: string): PillarKey[] {
  return activePillars(saju).filter((p) => pillarOf(saju, p)!.branch === b)
}

/* eslint-disable @typescript-eslint/no-explicit-any */

function pillarsOfPair(saju: SajuCalcResponse, v: any, pair: string[]): PillarKey[] {
  return (v.pillars as string[] | undefined)?.map((p) => p as PillarKey) ?? pair.flatMap((b) => findBranch(saju, b))
}

function buildPairEntries(saju: SajuCalcResponse, val: any[], kind: EntryKind): Entry[] {
  return val.map((v) => {
    const pair: string[] = v.pair ?? v
    const pillars = pillarsOfPair(saju, v, pair)
    return { kind, chars: pair, descPillars: v.pillars ? pillars : [], stems: [], branches: pillars }
  })
}

function buildStemEntries(val: any[], kind: EntryKind, nameOf: (v: any) => string, extra: (v: any) => Partial<Entry> = () => ({})): Entry[] {
  return val.map((v) => ({
    kind, chars: [nameOf(v)], descPillars: [], stems: (v.pillars as string[]).map((p) => p as PillarKey), branches: [], ...extra(v),
  }))
}

function buildGroupHap(saju: SajuCalcResponse, val: any, kind: EntryKind): Entry[] {
  return (Array.isArray(val) ? val : [val]).map((item) => ({
    kind,
    chars: [item.name ?? item.label ?? ''],
    descPillars: [],
    stems: [],
    branches: (item.branches ?? []).flatMap((b: string) => findBranch(saju, b)),
    resultEl: item.element,
  }))
}

/** 탭별 엔트리 빌드 (HapChungPanel.vue ENTRY_BUILDERS·entries 보존) — 구조화 데이터만 반환 */
export function buildEntries(saju: SajuCalcResponse, key: TabKey): Entry[] {
  if (key === 'gung_seong') return []
  const br = (saju.branch_relations ?? {}) as Record<string, any>
  const gm = saju.gong_mang ?? { vacant_branches: [], affected_pillars: [] }

  if (key === 'gong_mang') {
    return gm.affected_pillars.map((p) => {
      const pk = p as PillarKey
      return {
        kind: 'gongMang' as const,
        chars: [pillarOf(saju, pk)?.branch ?? ''],
        descPillars: [],
        pillar: pk,
        vacant: gm.vacant_branches,
        stems: [],
        branches: [pk],
      }
    })
  }

  const val = br[key]
  if (!val) return []

  switch (key) {
    case 'cheon_gan_hap':
      return buildStemEntries(val, 'stemHap', (x) => x.name ?? x.stems?.join(''), (x) => ({ resultEl: x.result_element }))
    case 'cheon_gan_chung':
      return buildStemEntries(val, 'stemChung', (x) => x.name)
    case 'yuk_hap':
      return (val as any[]).map((v) => {
        const pair: string[] = v.pair ?? []
        const pillars = pillarsOfPair(saju, v, pair)
        return { kind: 'yukHap' as const, chars: pair, descPillars: pillars, stems: [], branches: pillars, resultEl: v.element, broken: v.is_effective === false }
      })
    case 'sam_hap':
      return buildGroupHap(saju, val, 'samHap')
    case 'bang_hap':
      return buildGroupHap(saju, val, 'bangHap')
    case 'sam_hyeong':
      return (val as string[]).map((name) => ({ kind: 'samHyeong' as const, chars: [name], descPillars: [], stems: [], branches: (SAM_HYEONG[name] ?? []).flatMap((b) => findBranch(saju, b)) }))
    case 'chung':
      return buildPairEntries(saju, val, 'chung')
    case 'yuk_hae':
      return buildPairEntries(saju, val, 'yukHae')
    case 'pa':
      return buildPairEntries(saju, val, 'pa')
    case 'won_jin':
      return buildPairEntries(saju, val, 'wonJin')
    default:
      return []
  }
}

/** 탭에 표시할 데이터가 있는지 (HapChungPanel.vue hasData 보존) */
export function hasData(saju: SajuCalcResponse, key: TabKey): boolean {
  if (key === 'gung_seong') return true
  if (key === 'gong_mang') return (saju.gong_mang?.affected_pillars.length ?? 0) > 0
  const val = (saju.branch_relations as Record<string, any>)?.[key]
  if (!val) return false
  if (Array.isArray(val)) return val.length > 0
  if (typeof val === 'object') return Object.keys(val).length > 0
  return Boolean(val)
}
