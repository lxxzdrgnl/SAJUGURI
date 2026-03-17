<script setup lang="ts">
import type { SajuCalcResponse } from '~/types/saju'
import { useAuthStore } from '~/stores/auth'
import { STORAGE_KEYS } from '~/utils/storageKeys'

interface InputSummary {
  name: string
  date: string
  time: string
  gender: string
  city: string | null
}

const props = withDefaults(defineProps<{
  result: SajuCalcResponse
  inputSummary: InputSummary | null
  birthInput?: Record<string, unknown> | null
  initialSaved?: boolean
  fixedShareUrl?: string
}>(), {
  birthInput: null,
  initialSaved: false,
  fixedShareUrl: '',
})

const auth = useAuthStore()
const config = useRuntimeConfig()
const goToLogin = useGoToLogin()

// 깊은 복사로 Proxy 완전 해제 (Chart.js hasOwnProperty 오류 방지)
const raw = computed(() => JSON.parse(JSON.stringify(props.result)) as SajuCalcResponse)

// ── 오행 토글 ──────────────────────────────────────────────────────────────────
const applyHap  = ref(false)
const applyJohu = ref(false)

const PALACE_WEIGHTS: Record<string, Record<string, number>> = {
  year:  { stem: 1.0, branch: 1.0 },
  month: { stem: 1.0, branch: 2.0 },
  day:   { stem: 1.5, branch: 1.0 },
  hour:  { stem: 1.0, branch: 0.8 },
}

function applyPalaceWeights(
  chars: { pillar: string; type: string; element: string }[]
): Record<string, number> {
  const counts: Record<string, number> = { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 }
  for (const ch of chars) {
    if (!(ch.element in counts)) continue
    counts[ch.element] += PALACE_WEIGHTS[ch.pillar]?.[ch.type] ?? 1
  }
  const total = Object.values(counts).reduce((a, b) => a + b, 0)
  if (total === 0) return counts
  return Object.fromEntries(Object.entries(counts).map(([k, v]) => [k, Math.round((v / total) * 100)]))
}

// 합화 ratio + 궁성 가중치를 동시에 적용 (이진 변환 방지)
function applyPalaceWeightsWithHap(
  contributions: SajuCalcResponse['wuxing_hap_contributions']
): Record<string, number> {
  const counts: Record<string, number> = { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 }
  for (const c of contributions) {
    const w = PALACE_WEIGHTS[c.pillar]?.[c.type] ?? 1
    if (c.hap_element && c.hap_ratio > 0) {
      if (c.base_element in counts) counts[c.base_element] += w * (1 - c.hap_ratio)
      if (c.hap_element  in counts) counts[c.hap_element]  += w * c.hap_ratio
    } else {
      if (c.base_element in counts) counts[c.base_element] += w
    }
  }
  const total = Object.values(counts).reduce((a, b) => a + b, 0)
  if (total === 0) return counts
  return Object.fromEntries(Object.entries(counts).map(([k, v]) => [k, Math.round((v / total) * 100)]))
}

const wuxingPercent = computed((): Record<string, number> => {
  const r = raw.value
  if (!r) return {}
  if (applyJohu.value && applyHap.value) return applyPalaceWeightsWithHap(r.wuxing_hap_contributions)
  if (applyJohu.value) return applyPalaceWeights(r.wuxing_chars)
  return applyHap.value ? (r.wuxing_count_hap ?? r.wuxing_count) : r.wuxing_count
})

const sipseongPercent = computed(() => raw.value?.ten_gods_distribution ?? {})

// ── 격국 설명 ──────────────────────────────────────────────────────────────────
const GYEOK_DESC: Record<string, string> = {
  '정관격': '명예와 책임감이 강합니다. 원칙을 지키며 공직·대기업에서 인정받는 안정적인 격입니다.',
  '정재격': '성실하고 꾸준한 재물 축적형입니다. 안정적인 직장·사업을 선호하며 현실 감각이 탁월합니다.',
  '식신격': '온화하고 복록이 풍성합니다. 먹고 즐기는 여유가 있으며 예술적 감수성과 포용력이 뛰어납니다.',
  '정인격': '학문과 자비심이 깊습니다. 교육·의료·공직에서 두각을 나타내며 모성적 따뜻함이 있습니다.',
  '상관격': '뛰어난 표현력과 독창적 재능을 가집니다. 윗사람과 마찰이 있을 수 있으나 예술·전문직에서 빛납니다.',
  '편인격': '독특한 사고방식과 전문성을 가집니다. 연구·종교·예술·철학 분야에서 독보적인 성취를 이룹니다.',
  '편재격': '큰돈을 다루는 비즈니스 기질입니다. 투기·무역·사업에 강하며 활동력과 추진력이 넘칩니다.',
  '칠살격': '강한 통솔력과 행동력을 가집니다. 군경·정치·무술 등 권력 분야에서 두각을 나타냅니다.',
  '비견격': '독립심과 자존감이 강합니다. 혼자 힘으로 개척하며 동업보다 독자 사업이 맞습니다.',
  '겁재격': '강한 자아와 승부욕을 가집니다. 추진력 있게 일을 개척하지만 재물 관리에 신경 써야 합니다.',
  '종왕격': '오행이 비겁으로 쏠린 특수격입니다. 그 강한 기운을 따르면 크게 성공하고 거스르면 흉합니다.',
  '종살격': '오행이 관살로 쏠린 특수격입니다. 권력·조직 속에서 그 흐름을 따를 때 크게 성취합니다.',
  '종재격': '오행이 재성으로 쏠린 특수격입니다. 재물의 흐름을 따르면 큰 부를 이룰 수 있습니다.',
  '중화격': '어느 쪽으로도 치우치지 않는 균형 잡힌 격입니다. 다방면에 적응력이 높고 두루 유리합니다.',
}
const dayStemElement  = computed(() => raw.value?.day_pillar?.stem_element ?? '')
const dayStem         = computed(() => raw.value?.day_pillar?.stem ?? '')
const currentYear     = new Date().getFullYear()

// ── 합화 근거 ──────────────────────────────────────────────────────────────────
const PILLAR_LABEL: Record<string, Record<string, string>> = {
  year:  { stem: '연간', branch: '연지' },
  month: { stem: '월간', branch: '월지' },
  day:   { stem: '일간', branch: '일지' },
  hour:  { stem: '시간', branch: '시지' },
}
const HAP_TYPE_LABEL: Record<string, string> = {
  stem_hap: '천간합', yuk_hap: '육합', sam_hap: '삼합',
}

interface HapGroup { hapLabel: string; resultEl: string; items: { pos: string; from: string; to: string; ratio: number }[] }

const hapBasis = computed((): HapGroup[] => {
  const r = raw.value
  if (!r || !applyHap.value) return []
  const map = new Map<string, HapGroup>()
  for (const c of r.wuxing_hap_contributions) {
    if (!c.hap_element || c.hap_ratio <= 0) continue
    const key = `${c.hap_type}:${c.hap_element}`
    if (!map.has(key)) map.set(key, { hapLabel: HAP_TYPE_LABEL[c.hap_type ?? ''] ?? (c.hap_type ?? '합'), resultEl: c.hap_element, items: [] })
    map.get(key)!.items.push({
      pos: PILLAR_LABEL[c.pillar]?.[c.type] ?? c.pillar,
      from: c.base_element,
      to: c.hap_element,
      ratio: c.hap_ratio,
    })
  }
  return [...map.values()]
})

// ── 저장 상태 ─────────────────────────────────────────────────────────────────
const { saveState, saveProfile: _saveProfile, saveLabel, saveDisabled } = useProfileSave()
const showLoginModal = ref(false)

// ── 공유 상태 ─────────────────────────────────────────────────────────────────
const shareState = ref<'idle' | 'loading' | 'error'>('idle')
const shareUrl = ref('')
const showShareModal = ref(false)

onMounted(() => {
  if (props.initialSaved) saveState.value = 'exists'
  if (props.fixedShareUrl) shareUrl.value = props.fixedShareUrl
})

function buildProfileBody() {
  const b = props.birthInput!
  const dp = props.result.day_pillar
  return {
    name: (b.name as string)?.trim() || '내 사주',
    birth_date: b.birth_date as string,
    birth_time: (b.birth_time as string | null) ?? null,
    calendar: (b.calendar as string) ?? 'solar',
    gender: b.gender as string,
    is_leap_month: (b.is_leap_month as boolean) ?? false,
    city: (b.city as string | null) ?? null,
    longitude: ((b.birth_longitude ?? b.longitude) as number | null) ?? null,
    day_stem: dp?.stem ?? null,
    day_branch: dp?.branch ?? null,
    day_stem_element: dp?.stem_element ?? null,
  }
}

async function saveProfile() {
  if (!props.birthInput) return
  if (!auth.isLoggedIn) {
    localStorage.setItem(STORAGE_KEYS.SAJU_PENDING_SAVE, JSON.stringify(buildProfileBody()))
    showLoginModal.value = true
    return
  }
  await _saveProfile(buildProfileBody())
}

async function createShare() {
  if (shareUrl.value) {
    showShareModal.value = true
    return
  }
  shareState.value = 'loading'
  try {
    const data = await auth.authFetch<{ share_token: string; share_url: string }>(`${config.public.apiBase}/api/share`, {
      method: 'POST',
      body: { calc_snapshot: props.result, birth_input: props.birthInput },
    })
    shareUrl.value = data.share_url
    shareState.value = 'idle'
    showShareModal.value = true
  } catch {
    shareState.value = 'error'
    setTimeout(() => { shareState.value = 'idle' }, 2500)
  }
}


function confirmLogin() {
  // 로그인 후 결과 복원을 위해 현재 상태 저장
  if (import.meta.client && props.birthInput && props.result) {
    localStorage.setItem(STORAGE_KEYS.SAJU_PENDING_STATE, JSON.stringify({
      req: props.birthInput,
      res: props.result,
    }))
  }
  goToLogin()
}
</script>

<template>
  <div class="flex flex-col gap-8">

    <!-- 입력 요약 카드 -->
    <div v-if="inputSummary" class="input-summary-card">
      <div class="input-summary-fields">
        <div class="input-summary-field">
          <svg class="input-summary-icon" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.5"/>
            <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span class="input-summary-label">이름</span>
          <span class="input-summary-value">{{ inputSummary.name }}</span>
        </div>
        <div class="input-summary-field">
          <svg class="input-summary-icon" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="4" width="18" height="18" rx="3" stroke="currentColor" stroke-width="1.5"/>
            <path d="M3 9h18M8 2v4M16 2v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span class="input-summary-label">생년월일</span>
          <span class="input-summary-value">{{ inputSummary.date }}</span>
        </div>
        <div class="input-summary-field">
          <svg class="input-summary-icon" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/>
            <path d="M12 7v5l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span class="input-summary-label">생시</span>
          <span class="input-summary-value">{{ inputSummary.time }}</span>
        </div>
        <div class="input-summary-field">
          <svg class="input-summary-icon" viewBox="0 0 24 24" fill="none">
            <path d="M12 2C9 2 7 5 7 8c0 4 5 10 5 10s5-6 5-10c0-3-2-6-5-6z" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="12" cy="8" r="1.5" fill="currentColor"/>
          </svg>
          <span class="input-summary-label">성별</span>
          <span class="input-summary-value">{{ inputSummary.gender }}</span>
        </div>
        <div v-if="inputSummary.city" class="input-summary-field">
          <svg class="input-summary-icon" viewBox="0 0 24 24" fill="none">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="12" cy="9" r="2.5" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          <span class="input-summary-label">출생지</span>
          <span class="input-summary-value">{{ inputSummary.city }}</span>
        </div>
      </div>
      <!-- 부모가 주입하는 추가 액션 (예: 다시 계산 버튼) -->
      <slot name="summary-action" />
    </div>

    <!-- 구분선 -->
    <div class="animate-fade-up flex items-center gap-4">
      <div class="h-px flex-1" style="background: linear-gradient(to right, transparent, var(--border-default), transparent);"></div>
      <span class="fs-label tracking-[0.3em] uppercase" style="color: var(--text-muted);">분석 결과</span>
      <div class="h-px flex-1" style="background: linear-gradient(to left, transparent, var(--border-default), transparent);"></div>
    </div>

    <!-- 요약 배지 -->
    <div class="animate-fade-up animate-delay-100 flex flex-wrap gap-2">
      <span class="px-3 py-1 rounded-full fs-sub font-medium border"
        style="background: var(--surface-3); color: var(--text-primary); border-color: var(--border-default);">
        {{ raw.day_pillar.ganji_name }} 일주
      </span>
      <span class="px-3 py-1 rounded-full text-xs font-medium border"
        style="background: var(--surface-3); color: var(--text-primary); border-color: var(--border-default);">
        {{ raw.gyeok_guk.name }}
      </span>
      <span class="px-3 py-1 rounded-full text-xs font-medium border"
        style="background: var(--surface-3); color: var(--text-primary); border-color: var(--border-default);">
        용신 {{ raw.yong_sin.primary }} ({{ raw.yong_sin.yong_sin_label }})
      </span>
      <span class="px-3 py-1 rounded-full text-xs font-medium border"
        style="background: var(--surface-3); color: var(--text-primary); border-color: var(--border-default);">
        {{ raw.day_master_strength.level_8 }}
      </span>
      <span
        v-for="s in raw.sin_sals?.slice(0, 3)"
        :key="s.name"
        class="px-3 py-1 rounded-full fs-sub border"
        :style="s.type === 'lucky'
          ? `background: color-mix(in srgb, var(--color-good) 10%, transparent); color: var(--color-good); border-color: color-mix(in srgb, var(--color-good) 25%, transparent);`
          : s.type === 'unlucky' || s.type === 'warning'
            ? `background: color-mix(in srgb, var(--color-bad) 8%, transparent); color: var(--color-bad); border-color: color-mix(in srgb, var(--color-bad) 25%, transparent);`
            : 'background: var(--surface-3); color: var(--text-secondary); border-color: var(--border-subtle);'"
      >
        {{ s.name }}
      </span>
    </div>

    <!-- Section 1: 사주팔자 테이블 -->
    <section class="animate-fade-up animate-delay-200 space-y-2">
      <div class="flex items-center gap-1.5 pl-1">
        <span class="label-section">사주팔자 (四柱八字)</span>
        <UiInfoTooltip text="생년·월·일·시로 구성된 네 기둥 여덟 글자. 천간·지지·십성·12운성·신살을 포함합니다." />
      </div>
      <SajuTable :data="raw" />
      <SajuWuxingFeatureTable
        :dominant="raw.dominant_elements"
        :weak="raw.weak_elements"
      />
    </section>

    <!-- Section 2: 합충 분석 -->
    <section class="animate-fade-up animate-delay-300 space-y-2">
      <div class="flex items-center gap-1.5 pl-1">
        <span class="label-section">합충 분석 (合沖分析)</span>
        <UiInfoTooltip text="천간·지지 간의 합(合)과 충(沖) 관계. 합은 두 기운이 만나 변화하고, 충은 서로 부딪히는 것입니다. 합이라고 무조건 좋고, 충이라고 나쁜 것은 아닙니다." />
      </div>
      <SajuHapChungPanel :saju="raw" />
    </section>

    <!-- Section 3: 신살 -->
    <section class="animate-fade-up animate-delay-400 space-y-2">
      <div class="flex items-center gap-1.5 pl-1">
        <span class="label-section">신살 (神殺)</span>
        <UiInfoTooltip text="길흉화복에 영향을 주는 특별한 기운. 길신은 좋은 작용, 흉신은 주의가 필요한 작용을 합니다. 사주 전체 맥락에서 해석해야 합니다." />
      </div>
      <SajuSinSalTable :sin-sals="raw.sin_sals ?? []" />
    </section>

    <!-- Section 4: 오행 분석 -->
    <section class="animate-fade-up animate-delay-500 space-y-3">
      <div class="flex items-center gap-1.5 pl-1">
        <span class="label-section">오행 분석 (五行分析)</span>
        <UiInfoTooltip text="목·화·토·금·수 다섯 기운의 분포. 균형이 이상적이며, 부족하거나 과다한 오행은 용신 선정에 활용됩니다." />
      </div>

      <div class="flex flex-wrap gap-4 px-1">
        <label class="flex items-center gap-2 cursor-pointer select-none" @click="applyHap = !applyHap">
          <span
            class="w-4 h-4 rounded flex items-center justify-center border transition-all shrink-0"
            :style="applyHap
              ? 'background: var(--accent); border-color: var(--accent);'
              : 'background: var(--surface-1); border-color: var(--border-default);'"
          >
            <svg v-if="applyHap" class="w-2.5 h-2.5" viewBox="0 0 10 10" fill="none">
              <path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="fs-sub" style="color: var(--text-secondary);">합에 따른 오행 변화 적용</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer select-none" @click="applyJohu = !applyJohu">
          <span
            class="w-4 h-4 rounded flex items-center justify-center border transition-all shrink-0"
            :style="applyJohu
              ? 'background: var(--accent); border-color: var(--accent);'
              : 'background: var(--surface-1); border-color: var(--border-default);'"
          >
            <svg v-if="applyJohu" class="w-2.5 h-2.5" viewBox="0 0 10 10" fill="none">
              <path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="fs-sub" style="color: var(--text-secondary);">조후와 궁성 보정값 적용</span>
        </label>
      </div>

      <!-- 합화 / 궁성 근거 박스 -->
      <div
        v-if="(applyHap && hapBasis.length) || applyJohu"
        class="rounded-lg border p-3 flex flex-col gap-2"
        style="background: var(--surface-2); border-color: var(--border-subtle); font-size: 11px;"
      >
        <!-- 합화 근거 -->
        <div v-if="applyHap && hapBasis.length" class="flex flex-col gap-1.5">
          <span class="fs-label font-semibold" style="color: var(--text-secondary);">합화 적용</span>
          <div v-for="g in hapBasis" :key="g.hapLabel + g.resultEl" class="flex flex-wrap items-center gap-x-2 gap-y-1">
            <span
              class="shrink-0 px-1.5 py-0.5 rounded border text-[10px] font-semibold"
              :style="`color: var(--el-${g.resultEl}); background: color-mix(in srgb, var(--el-${g.resultEl}) 10%, transparent); border-color: color-mix(in srgb, var(--el-${g.resultEl}) 35%, transparent);`"
            >{{ g.hapLabel }} → {{ g.resultEl }}</span>
            <span v-for="item in g.items" :key="item.pos" class="flex items-center gap-0.5" style="color: var(--text-muted);">
              <span>{{ item.pos }}</span>
              <span class="opacity-50 mx-0.5">·</span>
              <span>{{ item.from }}→{{ item.to }}</span>
              <span class="opacity-60 ml-0.5">{{ Math.round(item.ratio * 100) }}%</span>
            </span>
          </div>
        </div>

        <!-- 구분선 -->
        <hr v-if="applyHap && hapBasis.length && applyJohu" style="border-color: var(--border-subtle);" />

        <!-- 궁성 가중치 근거 -->
        <div v-if="applyJohu" class="flex flex-col gap-1.5">
          <span class="fs-label font-semibold" style="color: var(--text-secondary);">궁성 가중치</span>
          <div class="flex flex-wrap gap-x-3 gap-y-1" style="color: var(--text-muted);">
            <span>월지 ×2.0</span>
            <span>일간 ×1.5</span>
            <span>연·월간·일지 ×1.0</span>
            <span>시지 ×0.8</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SajuWuxingPentagram :data="wuxingPercent" :day-element="dayStemElement" />
        <!-- 오행 분포 차트 + 균형 표 통합 카드 -->
        <div class="card p-0 overflow-hidden flex flex-col">
          <div class="px-5 pt-4 pb-2 flex items-center gap-1.5">
            <h3 class="label-section">오행 분포</h3>
            <UiInfoTooltip text="사주 여덟 글자에 담긴 목·화·토·금·수의 비율입니다. 합에 따른 오행 변화·궁성 보정을 적용하면 비율이 바뀝니다. 균형도는 각 오행이 20%에 가까울수록 높습니다." />
          </div>
          <div class="px-4 pb-2">
            <SajuWuxingDonutChart :data="wuxingPercent" />
          </div>
          <SajuWuxingBalanceTable :data="wuxingPercent" />
        </div>
      </div>
      <SajuSipseongDonutChart :data="sipseongPercent" />
    </section>

    <!-- Section 5: 강약 + 격국 + 용신 -->
    <section class="animate-fade-up animate-delay-600 space-y-2">
      <div class="flex items-center gap-1.5 pl-1">
        <span class="label-section">일간 강약 · 용신</span>
        <UiInfoTooltip text="일간의 힘의 세기(신강·신약)와 사주 균형을 맞추는 핵심 오행(用神). 득령·득지·득시·득세 여부로 강약을 판단합니다." />
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-4">
          <SajuStrengthBar :strength="raw.day_master_strength" />
          <SajuStrengthChart :strength="raw.day_master_strength" />
        </div>
        <div class="space-y-4">
          <div class="card">
            <div class="flex items-center gap-1.5 mb-3">
              <h3 class="label-section">격국 (格局)</h3>
              <UiInfoTooltip text="사주의 구조적 특성을 나타내는 틀(格). 월지를 중심으로 일간과의 관계를 분석하여 13종 중 하나로 판단합니다." />
            </div>
            <div class="flex flex-wrap gap-2 mb-3">
              <span class="px-4 py-2 rounded-xl font-bold text-base border"
                style="background: var(--surface-2); border-color: var(--border-default); color: var(--text-primary);">
                {{ raw.gyeok_guk.name }}
              </span>
              <span
                v-if="raw.gyeok_guk.basis"
                class="px-3 py-2 rounded-xl text-sm border"
                style="background: var(--surface-3); border-color: var(--border-subtle); color: var(--text-muted);"
              >
                {{ raw.gyeok_guk.basis }}
              </span>
            </div>
            <p v-if="GYEOK_DESC[raw.gyeok_guk.name]" class="fs-label leading-relaxed" style="color: var(--text-secondary);">
              {{ GYEOK_DESC[raw.gyeok_guk.name] }}
            </p>
          </div>
          <SajuYongSinBadge :yong-sin="raw.yong_sin" :wuxing-pct="wuxingPercent" />
        </div>
      </div>
    </section>

    <!-- Section 6: 대운 -->
    <section class="animate-fade-up animate-delay-700 space-y-2">
      <div class="flex items-center gap-1.5 pl-1">
        <span class="label-section">대운 (大運)</span>
        <UiInfoTooltip :text="`10년 단위로 바뀌는 운의 큰 흐름입니다. 이 사주는 ${raw.dae_un_start_age}세에 시작하여 10년 간격으로 바뀝니다.`" />
      </div>
      <SajuDaeUnSlider
        :dae-un-list="raw.dae_un_list"
        :current-dae-un="raw.current_dae_un"
        :start-age="raw.dae_un_start_age"
      />
    </section>

    <!-- Section 7: 연운 -->
    <section v-if="dayStem" class="animate-fade-up animate-delay-700 space-y-2">
      <div class="flex items-center gap-1.5 pl-1">
        <span class="label-section">연운 (年運)</span>
        <UiInfoTooltip text="해마다 바뀌는 1년 단위 운의 흐름. 해당 연도의 간지와 일간의 십성 관계로 해석합니다." />
      </div>
      <SajuYeonUnSlider :day-stem="dayStem" />
    </section>

    <!-- Section 8: 월운 -->
    <section v-if="dayStem" class="animate-fade-up animate-delay-700 space-y-2">
      <div class="flex items-center gap-1.5 pl-1">
        <span class="label-section">월운 (月運)</span>
        <UiInfoTooltip text="달마다 바뀌는 운의 흐름. 해당 월의 간지와 일간의 관계로 그 달의 기운을 판단합니다." />
      </div>
      <SajuWolUnSlider :year="currentYear" :day-stem="dayStem" />
    </section>

    <!-- Section 9: 일진 -->
    <section class="animate-fade-up animate-delay-700 space-y-2">
      <div class="flex items-center gap-1.5 pl-1">
        <span class="label-section">일진 (日辰)</span>
        <UiInfoTooltip text="하루하루의 간지(干支) 흐름. 해당 날의 천간·지지와 일간의 관계로 일별 기운을 확인합니다." />
      </div>
      <SajuIlJinCalendar />
    </section>

    <!-- 저장 / 공유 CTA 카드 -->
    <div v-if="birthInput" class="action-card">
      <div class="action-card-text">
        <p class="action-card-title">만세력 저장하기</p>
        <p class="action-card-desc">만세력을 저장하면 오늘의 운세·사주 상담에 바로 활용할 수 있어요.</p>
      </div>
      <div class="action-card-btns">
        <button class="action-btn action-btn-save" :disabled="saveDisabled" @click="saveProfile">
          <svg v-if="saveState === 'loading'" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="32" stroke-dashoffset="12"/>
          </svg>
          <svg v-else-if="saveState === 'done'" class="w-4 h-4" viewBox="0 0 24 24" fill="none">
            <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none">
            <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M17 21v-8H7v8M7 3v5h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ saveLabel }}</span>
        </button>

        <button class="action-btn action-btn-share" :disabled="shareState === 'loading'" @click="createShare">
          <svg v-if="shareState === 'loading'" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="32" stroke-dashoffset="12"/>
          </svg>
          <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none">
            <circle cx="18" cy="5" r="3" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="6" cy="12" r="3" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="18" cy="19" r="3" stroke="currentColor" stroke-width="1.5"/>
            <path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span>{{ shareState === 'error' ? '오류 발생' : '만세력 결과 공유하기' }}</span>
        </button>
      </div>
    </div>

    <!-- 부모가 추가하는 액션 슬롯 (예: share 페이지 CTA 카드) -->
    <slot name="actions" />

    <!-- 공유 모달 -->
    <UiShareModal v-model:show="showShareModal" :url="shareUrl" />

    <!-- 로그인 유도 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showLoginModal" class="modal-backdrop" @click.self="showLoginModal = false">
          <div class="modal-sheet">
            <div class="modal-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <p class="modal-title">로그인이 필요해요</p>
            <p class="modal-desc">만세력을 저장하려면 로그인이 필요해요.<br>로그인 후 자동으로 저장됩니다.</p>
            <div class="modal-actions">
              <button class="modal-btn modal-btn-primary" @click="confirmLogin">로그인하러 가기</button>
              <button class="modal-btn modal-btn-cancel" @click="showLoginModal = false">취소</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>
.input-summary-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px;
  border-radius: 14px;
  border: 1px solid var(--border-subtle);
  background: var(--surface-1);
}
.input-summary-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 32px;
  flex: 1;
}
.input-summary-field {
  display: flex;
  align-items: center;
  gap: 8px;
}
.input-summary-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: #8b5e30;
}
.input-summary-label {
  font-size: var(--fs-sub);
  color: #8b5e30;
  font-weight: 600;
  min-width: 48px;
  white-space: nowrap;
}
.input-summary-value {
  font-size: var(--fs-body);
  color: var(--text-primary);
  font-weight: 500;
}
@media (max-width: 640px) {
  .input-summary-card {
    flex-direction: column;
  }
  .input-summary-fields {
    grid-template-columns: 1fr;
    gap: 10px;
    width: 100%;
  }
}

/* ── 저장/공유 CTA 카드 ── */
.action-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 22px 24px;
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
  background: var(--surface-1);
}
.action-card-text {
  min-width: 0;
}
.action-card-title {
  font-size: var(--fs-body);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.action-card-desc {
  font-size: var(--fs-label);
  color: var(--text-muted);
  line-height: 1.6;
}
.action-card-btns {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: var(--fs-body);
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  border: 1px solid;
}
.action-btn:disabled { opacity: 0.55; cursor: default; }
.action-btn-save {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.action-btn-save:hover:not(:disabled) { background: var(--accent-hover); border-color: var(--accent-hover); }
.action-btn-share {
  background: var(--surface-1);
  color: var(--text-primary);
  border-color: var(--border-default);
}
.action-btn-share:hover:not(:disabled) { background: var(--surface-2); }

/* ── 모달 공통 ── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}
@media (min-width: 480px) { .modal-backdrop { align-items: center; } }
.modal-sheet {
  width: 100%;
  max-width: 440px;
  background: var(--surface-1);
  border-radius: 24px 24px 0 0;
  padding: 32px 24px 40px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: center;
}
@media (min-width: 480px) { .modal-sheet { border-radius: 24px; padding: 32px 28px; } }
.modal-sheet--left { text-align: left; }
.modal-icon {
  width: 48px; height: 48px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  display: flex; align-items: center; justify-content: center;
  color: var(--accent);
  margin: 0 auto 4px;
}
.modal-icon svg { width: 24px; height: 24px; }
.modal-header { display: flex; align-items: center; justify-content: space-between; }
.modal-title { font-size: 18px; font-weight: 800; color: var(--text-primary); }
.modal-subdesc { font-size: var(--fs-sub); color: var(--text-muted); }
.modal-desc { font-size: var(--fs-sub); color: var(--text-muted); line-height: 1.7; margin-bottom: 6px; }
.modal-close {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border: none; background: var(--surface-2);
  border-radius: 8px; cursor: pointer; color: var(--text-muted); flex-shrink: 0;
}
.modal-close svg { width: 16px; height: 16px; }
.modal-close:hover { background: var(--surface-3); }
.modal-link-box {
  background: var(--surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 12px 14px;
}
.modal-link-text { font-size: 13px; color: var(--text-secondary); word-break: break-all; display: block; }
.modal-copy-btn {
  display: flex; align-items: center; justify-content: center;
  gap: 8px; width: 100%; padding: 13px; border-radius: 12px;
  border: none; background: var(--accent); color: #fff;
  font-size: var(--fs-body); font-weight: 600; font-family: inherit;
  cursor: pointer; transition: background 0.15s; margin-top: 4px;
}
.modal-copy-btn:hover { background: var(--accent-hover); }
.modal-actions { display: flex; flex-direction: column; gap: 8px; width: 100%; margin-top: 4px; }
.modal-btn {
  width: 100%; padding: 14px; border-radius: 12px;
  font-size: var(--fs-body); font-weight: 600; font-family: inherit;
  cursor: pointer; border: none; transition: background 0.15s;
}
.modal-btn-primary { background: var(--accent); color: #fff; }
.modal-btn-primary:hover { background: var(--accent-hover); }
.modal-btn-cancel { background: var(--surface-2); color: var(--text-secondary); }
.modal-btn-cancel:hover { background: var(--surface-3); }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .modal-sheet, .modal-leave-active .modal-sheet { transition: transform 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-sheet, .modal-leave-to .modal-sheet { transform: translateY(40px); }
</style>
