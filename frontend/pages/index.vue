<script setup lang="ts">
import type { SajuCalcRequest } from '~/types/saju'
import { useSajuStore } from '~/stores/saju'

const store = useSajuStore()

async function onSubmit(req: SajuCalcRequest) {
  await store.calculate(req)
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center py-12 px-4">
    <!-- 헤더 -->
    <header class="mb-10 text-center">
      <h1 class="text-3xl font-bold text-white tracking-tight">
        <span class="text-indigo-400">사주</span>본
      </h1>
      <p class="mt-1 text-sm text-gray-500">AI 사주 상담 — Headline-Driven Insights</p>
    </header>

    <!-- 입력 폼 -->
    <SajuInputForm @submit="onSubmit" />

    <!-- 로딩 -->
    <div v-if="store.loading" class="mt-10 flex items-center gap-3 text-indigo-400">
      <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
      <span>사주를 계산하는 중...</span>
    </div>

    <!-- 에러 -->
    <div v-if="store.error" class="mt-6 card border-red-800/50 text-red-400 max-w-lg w-full text-sm">
      {{ store.error }}
    </div>

    <!-- 결과 — 4기둥 미리보기 (Phase 3 컴포넌트로 교체 예정) -->
    <div v-if="store.result && !store.loading" class="mt-8 max-w-2xl w-full space-y-4">
      <!-- 요약 배지 -->
      <div class="card flex flex-wrap gap-3 text-sm">
        <span class="px-3 py-1 rounded-full bg-indigo-900/60 text-indigo-300">
          {{ store.result.day_pillar.ganji_name }} 일주
        </span>
        <span class="px-3 py-1 rounded-full bg-purple-900/60 text-purple-300">
          {{ store.result.gyeok_guk.name }}
        </span>
        <span class="px-3 py-1 rounded-full bg-sky-900/60 text-sky-300">
          용신 {{ store.result.yong_sin.primary }} ({{ store.result.yong_sin.yong_sin_label }})
        </span>
        <span class="px-3 py-1 rounded-full bg-emerald-900/60 text-emerald-300">
          {{ store.result.day_master_strength.level_8 }}
        </span>
      </div>

      <!-- 4기둥 그리드 (간단 버전) -->
      <div class="card">
        <h3 class="text-sm text-gray-400 mb-3">사주팔자</h3>
        <div class="grid grid-cols-4 gap-2 text-center">
          <div
            v-for="(key, i) in ['year_pillar','month_pillar','day_pillar','hour_pillar'] as const"
            :key="key"
            class="bg-[#0f0f1a] rounded-lg p-3 space-y-1"
          >
            <div class="text-xs text-gray-500">{{ ['연주','월주','일주','시주'][i] }}</div>
            <div class="text-lg font-bold" :class="`element-${store.result[key].stem_element}`">
              {{ store.result[key].stem }}
            </div>
            <div class="text-xs text-gray-400">{{ store.result[key].stem_ten_god }}</div>
            <div class="text-lg font-bold" :class="`element-${store.result[key].branch_element}`">
              {{ store.result[key].branch }}
            </div>
            <div class="text-xs text-gray-400">{{ store.result[key].twelve_wun }}</div>
            <div v-if="store.result[key].twelve_sin_sal" class="text-xs text-yellow-500">
              {{ store.result[key].twelve_sin_sal }}
            </div>
          </div>
        </div>
      </div>

      <!-- 득령/득지/득시/득세 -->
      <div class="card">
        <h3 class="text-sm text-gray-400 mb-3">득령 · 득지 · 득시 · 득세</h3>
        <div class="flex gap-4">
          <span
            v-for="[label, val] in [
              ['득령', store.result.day_master_strength.deuk_ryeong],
              ['득지', store.result.day_master_strength.deuk_ji],
              ['득시', store.result.day_master_strength.deuk_si],
              ['득세', store.result.day_master_strength.deuk_se],
            ]"
            :key="label as string"
            class="flex flex-col items-center gap-1"
          >
            <span class="text-xs text-gray-400">{{ label }}</span>
            <span :class="val ? 'text-emerald-400' : 'text-gray-600'" class="text-lg font-bold">
              {{ val ? '○' : '✗' }}
            </span>
          </span>
        </div>
      </div>

      <!-- 공망 -->
      <div v-if="store.result.gong_mang.vacant_branches.length" class="card text-sm">
        <h3 class="text-gray-400 mb-1">공망(空亡)</h3>
        <span class="text-yellow-400">
          {{ store.result.gong_mang.vacant_branches.join(' · ') }}
          <template v-if="store.result.gong_mang.affected_pillars.length">
            — 해당 기둥: {{ store.result.gong_mang.affected_pillars.join(', ') }}
          </template>
        </span>
      </div>

      <!-- 신살 -->
      <div v-if="store.result.sin_sals.length" class="card">
        <h3 class="text-sm text-gray-400 mb-2">신살</h3>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="s in store.result.sin_sals"
            :key="s.name"
            :class="{
              'bg-red-900/50 text-red-300':   s.type === 'unlucky' || s.type === 'warning',
              'bg-green-900/50 text-green-300': s.type === 'lucky',
              'bg-gray-800 text-gray-400':    s.type === 'neutral',
            }"
            class="px-2 py-0.5 rounded text-xs"
          >
            {{ s.name }}
          </span>
        </div>
      </div>

      <!-- 대운 -->
      <div class="card">
        <h3 class="text-sm text-gray-400 mb-3">대운 ({{ store.result.dae_un_start_age }}세 ~)</h3>
        <div class="flex gap-2 overflow-x-auto pb-1">
          <div
            v-for="d in store.result.dae_un_list"
            :key="d.start_age"
            :class="d.start_age === store.result.current_dae_un.start_age ? 'border-indigo-500' : 'border-gray-700'"
            class="min-w-[60px] border rounded-lg p-2 text-center text-xs flex-shrink-0"
          >
            <div class="text-gray-400 mb-1">{{ d.start_age }}세</div>
            <div :class="`element-${d.stem_element}`" class="font-bold">{{ d.stem }}</div>
            <div :class="`element-${d.branch_element}`" class="font-bold">{{ d.branch }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
