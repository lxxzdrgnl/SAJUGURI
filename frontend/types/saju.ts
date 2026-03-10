/** 사주 계산 요청 */
export interface SajuCalcRequest {
  birth_date: string        // 'YYYY-MM-DD'
  birth_time: string        // 'HH:MM'
  gender: 'male' | 'female'
  calendar?: 'solar' | 'lunar'
  is_leap_month?: boolean
}

/** 기둥 하나 */
export interface Pillar {
  stem: string
  branch: string
  stem_element: string
  branch_element: string
  yin_yang: string
  ganji_name: string
  stem_ten_god: string
  branch_ten_god: string
  twelve_wun: string
  twelve_sin_sal: string
}

/** 일간 강약 */
export interface DayMasterStrength {
  score: number
  level: 'very_strong' | 'strong' | 'medium' | 'weak' | 'very_weak'
  level_8: string
  deuk_ryeong: boolean
  deuk_ji: boolean
  deuk_si: boolean
  deuk_se: boolean
}

/** 용신 */
export interface YongSin {
  primary: string
  secondary: string | null
  xi_sin: string[]
  ji_sin: string[]
  logic_type: string
  yong_sin_label: string
  reasoning_priority: string
}

/** 대운 한 구간 */
export interface DaeUnEntry {
  start_age: number
  end_age: number
  stem: string
  branch: string
  stem_element: string
  branch_element: string
  ganji_name: string
  stem_ten_god?: string
  branch_ten_god?: string
}

/** 신살 */
export interface SinSal {
  name: string
  type: 'lucky' | 'neutral' | 'unlucky' | 'warning'
  priority: 'high' | 'medium' | 'low'
  location: string[]
  description?: string
}

/** 공망 */
export interface GongMang {
  vacant_branches: string[]
  affected_pillars: string[]
}

/** 사주 계산 응답 */
export interface SajuCalcResponse {
  meta: {
    gender: string
    birth_date: string
    birth_time: string
    calendar: string
    time_correction_minutes: number
    applied_time: string
    timezone_note: string
    climate_vibe: {
      season: string
      temperature: string
      humidity: string
      month_element: string
      day_element_relation: string
    }
  }
  day_master_strength: DayMasterStrength
  yong_sin: YongSin
  gyeok_guk: { name: string; basis: string }
  year_pillar: Pillar
  month_pillar: Pillar
  day_pillar: Pillar
  hour_pillar: Pillar
  wuxing_count: Record<string, number>
  dominant_elements: string[]
  weak_elements: string[]
  yin_yang_ratio: { yang: number; yin: number }
  ten_gods_distribution: Record<string, number>
  ten_gods_void_info: Array<{ category: string; hidden_in_ji_jang_gan: Record<string, string[]> }>
  structure_patterns: unknown[]
  gong_mang: GongMang
  sin_sals: SinSal[]
  branch_relations: Record<string, unknown>
  ji_jang_gan: Record<string, string[]>
  dae_un_start_age: number
  dae_un_list: DaeUnEntry[]
  current_dae_un: DaeUnEntry
  dynamics: unknown
  synergy: unknown[]
  behavior_profile: unknown
  context_ranking: unknown
  life_domains: unknown
}

/** 월운 항목 */
export interface WolUnEntry {
  month: number
  stem: string
  branch: string
  stem_element: string
  branch_element: string
  ganji_name: string
  stem_ten_god: string
  branch_ten_god: string
  twelve_wun: string
}

/** 일진 항목 */
export interface IlJinEntry {
  date: string
  stem: string
  branch: string
  ganji_name: string
  lunar_month: number
  lunar_day: number
  is_leap_month: boolean
  solar_term?: string
}
