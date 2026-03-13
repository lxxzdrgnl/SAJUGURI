<script setup lang="ts">
import type { SajuCalcResponse } from '~/types/saju'

interface InputSummary {
  name: string
  date: string
  time: string
  gender: string
  city: string | null
}

const props = defineProps<{
  result: SajuCalcResponse
  inputSummary: InputSummary | null
}>()

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
    const w = PALACE_WEIGHTS[ch.pillar]?.[ch.type] ?? 1
    counts[ch.element] += w
  }
  const total = Object.values(counts).reduce((a, b) => a + b, 0)
  if (total === 0) return counts
  const out: Record<string, number> = {}
  for (const [k, v] of Object.entries(counts)) {
    out[k] = Math.round((v / total) * 100)
  }
  return out
}

const wuxingPercent = computed((): Record<string, number> => {
  const r = raw.value
  if (!r) return {}
  if (applyJohu.value) {
    const chars = applyHap.value ? r.wuxing_chars_hap : r.wuxing_chars
    return applyPalaceWeights(chars ?? [])
  }
  return applyHap.value ? (r.wuxing_count_hap ?? r.wuxing_count) : r.wuxing_count
})

const sipseongPercent = computed(() => raw.value?.ten_gods_distribution ?? {})
const dayStemElement  = computed(() => raw.value?.day_pillar?.stem_element ?? '')
const dayStem         = computed(() => raw.value?.day_pillar?.stem ?? '')
const currentYear     = new Date().getFullYear()
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

      <div v-if="applyJohu" class="flex flex-wrap gap-x-3 gap-y-1 px-1" style="font-size: 11px; color: var(--text-muted);">
        <span>월지 ×2.0</span>
        <span>일간 ×1.5</span>
        <span>연·월간·일지 ×1.0</span>
        <span>시지 ×0.8</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SajuWuxingPentagram :data="wuxingPercent" :day-element="dayStemElement" />
        <SajuWuxingDonutChart :data="wuxingPercent" />
        <SajuSipseongDonutChart :data="sipseongPercent" />
      </div>
      <SajuWuxingBalanceTable :data="wuxingPercent" />
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
            <div class="flex flex-wrap gap-2">
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
          </div>
          <SajuYongSinBadge :yong-sin="raw.yong_sin" />
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

    <!-- 하단 액션 슬롯 (저장/공유 or CTA) -->
    <slot name="actions" />

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
</style>
