<script setup lang="ts">
import type { SajuCalcRequest } from '~/types/saju'
import { useSajuStore } from '~/stores/saju'

const store = useSajuStore()

async function onSubmit(req: SajuCalcRequest) {
  await store.calculate(req)
}

// ── 오행 분석 토글 ────────────────────────────────────────────────────────────
const applyHap   = ref(false)  // 합에 따른 오행 변화 (백엔드 wuxing_count_hap 사용)
const applyJohu  = ref(false)  // 궁성·조후 가중치 (UI 표시 옵션)

// 궁성(宮星) 위치 가중치 — 표시 전용 옵션 (DB 저장 안 함)
const PALACE_WEIGHTS: Record<string, Record<string, number>> = {
  year:  { stem: 1.0, branch: 1.0 },
  month: { stem: 1.0, branch: 2.0 },
  day:   { stem: 1.5, branch: 1.0 },
  hour:  { stem: 1.0, branch: 0.8 },
}

// 궁성 가중치 적용 (백엔드 wuxing_chars / wuxing_chars_hap 기반)
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

// 최종 오행 퍼센트 — 합화/궁성 토글 반영 (합화는 백엔드 계산값 사용)
const wuxingPercent = computed((): Record<string, number> => {
  const r = store.result
  if (!r) return {}
  if (applyJohu.value) {
    // 궁성 가중치: 백엔드 위치별 ohaeng 목록 기반으로 재계산
    const chars = applyHap.value ? r.wuxing_chars_hap : r.wuxing_chars
    return applyPalaceWeights(chars ?? [])
  }
  // 기본: 백엔드 퍼센트 그대로 사용
  return applyHap.value ? (r.wuxing_count_hap ?? r.wuxing_count) : r.wuxing_count
})

// 십성 퍼센트 — 백엔드가 이미 퍼센트로 반환
const sipseongPercent = computed(() => store.result?.ten_gods_distribution ?? {})

// 일간 오행
const dayStemElement = computed(() => store.result?.day_pillar?.stem_element ?? '')
// 일간 천간 (월운·연운 슬라이더용)
const dayStem = computed(() => store.result?.day_pillar?.stem ?? '')
// 현재 연도
const currentYear = new Date().getFullYear()
</script>

<template>
  <div class="flex flex-col py-10 px-4">

    <!-- ── 헤더 ── -->
    <header
      class="text-center transition-all duration-500"
      :class="store.result ? 'mb-6' : 'mb-12'"
    >
      <div class="inline-block">
        <h1
          class="font-serif font-bold tracking-wide leading-none"
          :class="store.result ? 'text-3xl' : 'text-5xl'"
          style="transition: font-size 0.4s ease; color: #1a1a1a;"
        >
          <span style="color: #3a3a3a;">사주</span><span style="color: #a67c52;">본</span>
        </h1>
        <div
          v-if="!store.result"
          class="mt-1 text-[10px] tracking-[0.35em] uppercase"
          style="color: #aaaaaa;"
        >
          四柱八字 · AI 사주 상담
        </div>
      </div>
      <p
        v-if="!store.result"
        class="mt-4 text-sm"
        style="color: #888888;"
      >
        오직 그 사람만을 위한 결론형 사주 리포트
      </p>
    </header>

    <!-- ── 입력 폼 ── -->
    <div
      class="w-full mx-auto transition-all duration-500"
      :class="store.result ? 'max-w-3xl' : 'max-w-md'"
    >
      <SajuInputForm @submit="onSubmit" />
    </div>

    <!-- ── 로딩 ── -->
    <div v-if="store.loading" class="mt-12 flex flex-col items-center gap-4" style="color: #888888;">
      <div class="relative w-10 h-10">
        <svg class="animate-spin w-10 h-10 absolute inset-0" viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="17" stroke="#e8e2db" stroke-width="3"/>
          <path d="M20 3a17 17 0 0 1 17 17" stroke="#3a3a3a" stroke-width="3" stroke-linecap="round"/>
        </svg>
      </div>
      <span class="text-sm tracking-wide" style="color: #888888;">사주를 계산하는 중...</span>
    </div>

    <!-- ── 에러 ── -->
    <div
      v-if="store.error"
      class="mt-6 max-w-xl mx-auto w-full rounded-xl px-5 py-4 text-sm"
      style="background: rgba(212,63,63,0.05); border: 1px solid rgba(212,63,63,0.18); color: #c03030;"
    >
      {{ store.error }}
    </div>

    <!-- ── 결과 ── -->
    <div
      v-if="store.result && !store.loading"
      class="mt-10 max-w-5xl w-full mx-auto space-y-8"
    >

      <!-- 구분선 -->
      <div class="flex items-center gap-4">
        <div class="h-px flex-1" style="background: linear-gradient(to right, transparent, #ddd7d0, transparent);"></div>
        <span class="fs-label tracking-[0.3em] uppercase" style="color: #aaaaaa;">분석 결과</span>
        <div class="h-px flex-1" style="background: linear-gradient(to left, transparent, #ddd7d0, transparent);"></div>
      </div>

      <!-- 요약 배지 행 -->
      <div class="animate-fade-up flex flex-wrap gap-2">
        <span
          class="px-3 py-1 rounded-full fs-sub font-medium border"
          style="background: #f0ece8; color: #3a3a3a; border-color: #ddd7d0;"
        >
          {{ store.result.day_pillar.ganji_name }} 일주
        </span>
        <span
          class="px-3 py-1 rounded-full text-xs font-medium border"
          style="background: #f0ece8; color: #3a3a3a; border-color: #ddd7d0;"
        >
          {{ store.result.gyeok_guk.name }}
        </span>
        <span
          class="px-3 py-1 rounded-full text-xs font-medium border"
          style="background: #f0ece8; color: #3a3a3a; border-color: #ddd7d0;"
        >
          용신 {{ store.result.yong_sin.primary }} ({{ store.result.yong_sin.yong_sin_label }})
        </span>
        <span
          class="px-3 py-1 rounded-full text-xs font-medium border"
          style="background: #f0ece8; color: #3a3a3a; border-color: #ddd7d0;"
        >
          {{ store.result.day_master_strength.level_8 }}
        </span>
        <!-- 신살 요약 — 길(吉)=목색, 흉(凶)=화색, 중립=회색 -->
        <span
          v-for="s in store.result.sin_sals?.slice(0, 3)"
          :key="s.name"
          class="px-3 py-1 rounded-full fs-sub border"
          :style="s.type === 'lucky'
            ? `background: color-mix(in srgb, var(--el-목) 8%, transparent); color: var(--el-목); border-color: color-mix(in srgb, var(--el-목) 25%, transparent);`
            : s.type === 'unlucky' || s.type === 'warning'
              ? `background: color-mix(in srgb, var(--el-화) 8%, transparent); color: var(--el-화); border-color: color-mix(in srgb, var(--el-화) 25%, transparent);`
              : 'background: #f0ece8; color: #666666; border-color: #e8e2db;'"
        >
          {{ s.name }}
        </span>
      </div>

      <!-- Section 1: 사주팔자 테이블 -->
      <section class="animate-fade-up animate-delay-100 space-y-2">
        <div class="flex items-center gap-1.5 pl-1">
          <span class="label-section">사주팔자 (四柱八字)</span>
          <UiInfoTooltip text="생년·월·일·시로 구성된 네 기둥 여덟 글자. 천간·지지·십성·12운성·신살을 포함합니다." />
        </div>
        <SajuTable :data="store.result" />
      </section>

      <!-- Section 2: 합충 분석 -->
      <section class="animate-fade-up animate-delay-200 space-y-2">
        <div class="flex items-center gap-1.5 pl-1">
          <span class="label-section">합충 분석 (合沖分析)</span>
          <UiInfoTooltip text="천간·지지 간의 합(合)과 충(沖) 관계. 합은 두 기운이 만나 변화하고, 충은 서로 부딪히는 것입니다. 합이라고 무조건 좋고, 충이라고 나쁜 것은 아닙니다." />
        </div>
        <SajuHapChungPanel :saju="store.result" />
      </section>

      <!-- Section 3: 신살 -->
      <section class="animate-fade-up animate-delay-300 space-y-2">
        <div class="flex items-center gap-1.5 pl-1">
          <span class="label-section">신살 (神殺)</span>
          <UiInfoTooltip text="길흉화복에 영향을 주는 특별한 기운. 길신은 좋은 작용, 실성(흉신)은 주의가 필요한 작용을 합니다. 사주 전체 맥락에서 해석해야 합니다." />
        </div>
        <SajuSinSalTable :sin-sals="store.result.sin_sals ?? []" />
      </section>

      <!-- Section 4: 오행 분석 -->
      <section class="animate-fade-up animate-delay-400 space-y-3">
        <div class="flex items-center gap-1.5 pl-1">
          <span class="label-section">오행 분석 (五行分析)</span>
          <UiInfoTooltip text="목·화·토·금·수 다섯 기운의 분포. 균형이 이상적이며, 부족하거나 과다한 오행은 용신 선정에 활용됩니다." />
        </div>

        <!-- 토글 옵션 -->
        <div class="flex flex-wrap gap-4 px-1">
          <!-- 합화 토글 -->
          <label class="flex items-center gap-2 cursor-pointer select-none" @click="applyHap = !applyHap">
            <span
              class="w-4 h-4 rounded flex items-center justify-center border transition-all shrink-0"
              :style="applyHap
                ? 'background: #3a3a3a; border-color: #3a3a3a;'
                : 'background: #ffffff; border-color: #d0cac4;'"
            >
              <svg v-if="applyHap" class="w-2.5 h-2.5" viewBox="0 0 10 10" fill="none">
                <path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
            <span class="fs-sub" style="color: #666666;">합에 따른 오행 변화 적용</span>
          </label>

          <!-- 궁성·조후 토글 -->
          <label class="flex items-center gap-2 cursor-pointer select-none" @click="applyJohu = !applyJohu">
            <span
              class="w-4 h-4 rounded flex items-center justify-center border transition-all shrink-0"
              :style="applyJohu
                ? 'background: #3a3a3a; border-color: #3a3a3a;'
                : 'background: #ffffff; border-color: #d0cac4;'"
            >
              <svg v-if="applyJohu" class="w-2.5 h-2.5" viewBox="0 0 10 10" fill="none">
                <path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
            <span class="fs-sub" style="color: #666666;">조후와 궁성 보정값 적용</span>
          </label>
        </div>

        <!-- 가중치 안내 (펼침) -->
        <div v-if="applyJohu" class="flex flex-wrap gap-x-3 gap-y-1 px-1" style="font-size: 11px; color: #aaaaaa;">
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

      <!-- Section 5: 강약 바 + 용신·격국 2열 -->
      <section class="animate-fade-up animate-delay-500 space-y-2">
        <div class="flex items-center gap-1.5 pl-1">
          <span class="label-section">일간 강약 · 용신</span>
          <UiInfoTooltip text="일간의 힘의 세기(신강·신약)와 사주 균형을 맞추는 핵심 오행(用神). 득령·득지·득시·득세 여부로 강약을 판단합니다." />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-4">
            <SajuStrengthBar :strength="store.result.day_master_strength" />
            <SajuStrengthChart :strength="store.result.day_master_strength" />
          </div>

          <div class="space-y-4">
            <!-- 격국 배지 -->
            <div class="card">
              <div class="flex items-center gap-1.5 mb-3">
                <h3 class="label-section">격국 (格局)</h3>
                <UiInfoTooltip text="사주의 구조적 특성을 나타내는 틀(格). 월지를 중심으로 일간과의 관계를 분석하여 13종 중 하나로 판단합니다." />
              </div>
              <div class="flex flex-wrap gap-2">
                <span
                  class="px-4 py-2 rounded-xl font-bold text-base border"
                  style="background: #f7f4f1; border-color: #ddd7d0; color: #3a3a3a;"
                >
                  {{ store.result.gyeok_guk.name }}
                </span>
                <span
                  v-if="store.result.gyeok_guk.basis"
                  class="px-3 py-2 rounded-xl text-sm border"
                  style="background: #f0ece8; border-color: #e8e2db; color: #888888;"
                >
                  {{ store.result.gyeok_guk.basis }}
                </span>
              </div>
            </div>
            <!-- 용신 배지 -->
            <SajuYongSinBadge :yong-sin="store.result.yong_sin" />
          </div>
        </div>
      </section>

      <!-- Section 6: 대운 슬라이더 -->
      <section class="animate-fade-up animate-delay-600 space-y-2">
        <div class="flex items-center gap-1.5 pl-1">
          <span class="label-section">대운 (大運)</span>
          <UiInfoTooltip text="10년 단위로 바뀌는 운의 큰 흐름. 절기 기준 3일이 1년에 해당하며, 태어난 성별과 연주 음양에 따라 순행·역행이 결정됩니다." />
        </div>
        <SajuDaeUnSlider
          :dae-un-list="store.result.dae_un_list"
          :current-dae-un="store.result.current_dae_un"
          :start-age="store.result.dae_un_start_age"
        />
      </section>

      <!-- Section 7: 연운 슬라이더 -->
      <section v-if="dayStem" class="animate-fade-up animate-delay-700 space-y-2">
        <div class="flex items-center gap-1.5 pl-1">
          <span class="label-section">연운 (年運)</span>
          <UiInfoTooltip text="해마다 바뀌는 1년 단위 운의 흐름. 해당 연도의 간지와 일간의 십성 관계로 해석합니다." />
        </div>
        <SajuYeonUnSlider :day-stem="dayStem" />
      </section>

      <!-- Section 8: 월운 슬라이더 -->
      <section v-if="dayStem" class="animate-fade-up animate-delay-700 space-y-2">
        <div class="flex items-center gap-1.5 pl-1">
          <span class="label-section">월운 (月運)</span>
          <UiInfoTooltip text="달마다 바뀌는 운의 흐름. 해당 월의 간지와 일간의 관계로 그 달의 기운을 판단합니다." />
        </div>
        <SajuWolUnSlider :year="currentYear" :day-stem="dayStem" />
      </section>

      <!-- Section 9: 일진 달력 -->
      <section class="animate-fade-up animate-delay-700 space-y-2">
        <div class="flex items-center gap-1.5 pl-1">
          <span class="label-section">일진 (日辰)</span>
          <UiInfoTooltip text="하루하루의 간지(干支) 흐름. 해당 날의 천간·지지와 일간의 관계로 일별 기운을 확인합니다." />
        </div>
        <SajuIlJinCalendar />
      </section>

    </div>
  </div>
</template>
