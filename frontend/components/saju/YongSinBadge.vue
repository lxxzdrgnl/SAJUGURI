<script setup lang="ts">
import type { YongSin } from '~/types/saju'

defineProps<{
  yongSin: YongSin
}>()

// 오행 → 색상 (utils/elementColor.ts auto-import)
function dotColor(el: string) { return elColor(el) }
</script>

<template>
  <div class="card space-y-4">
    <h3 class="label-section">용신 · 희신 · 기신 (用神)</h3>

    <!-- 용신 (primary) -->
    <div class="flex items-center gap-3">
      <span class="text-xs w-10 shrink-0" style="color: #aaaaaa;">용신</span>
      <div
        class="flex items-center gap-2 px-4 py-2 rounded-lg border"
        style="background: rgba(40,120,200,0.06); border-color: rgba(40,120,200,0.2);"
      >
        <span
          class="w-3 h-3 rounded-full shrink-0"
          :style="{ backgroundColor: dotColor(yongSin.primary) }"
        />
        <span class="text-base font-bold" style="color: #1a1a1a;">{{ yongSin.primary }}</span>
      </div>
      <div
        v-if="yongSin.secondary"
        class="flex items-center gap-2 px-3 py-2 rounded-lg border"
        style="background: #f7f4f1; border-color: #e8e2db;"
      >
        <span
          class="w-2.5 h-2.5 rounded-full shrink-0"
          :style="{ backgroundColor: dotColor(yongSin.secondary) }"
        />
        <span class="text-sm" style="color: #666666;">{{ yongSin.secondary }}</span>
      </div>
    </div>

    <!-- 희신 (xi_sin) -->
    <div v-if="yongSin.xi_sin?.length" class="flex items-center gap-3">
      <span class="text-xs w-10 shrink-0" style="color: #aaaaaa;">희신</span>
      <div class="flex gap-2 flex-wrap">
        <div
          v-for="el in yongSin.xi_sin"
          :key="el"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border"
          :style="elBgStyle(el)"
        >
          <span
            class="w-2.5 h-2.5 rounded-full shrink-0"
            :style="{ backgroundColor: dotColor(el) }"
          />
          <span class="text-sm font-medium" :style="`color: ${dotColor(el)};`">{{ el }}</span>
        </div>
      </div>
    </div>

    <!-- 기신 (ji_sin) — 각 오행 고유색 사용 -->
    <div v-if="yongSin.ji_sin?.length" class="flex items-center gap-3">
      <span class="text-xs w-10 shrink-0" style="color: #aaaaaa;">기신</span>
      <div class="flex gap-2 flex-wrap">
        <div
          v-for="el in yongSin.ji_sin"
          :key="el"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border"
          :style="elBgStyle(el)"
        >
          <span
            class="w-2.5 h-2.5 rounded-full shrink-0"
            :style="{ backgroundColor: dotColor(el) }"
          />
          <span class="text-sm font-medium" :style="`color: ${dotColor(el)};`">{{ el }}</span>
        </div>
      </div>
    </div>

    <!-- 구분선 -->
    <div class="pt-3 flex flex-wrap gap-2" style="border-top: 1px solid #f0ece8;">
      <!-- 용신 레이블 -->
      <span
        v-if="yongSin.yong_sin_label"
        class="px-2.5 py-1 text-xs rounded-full border"
        style="background: #f0ece8; color: #888888; border-color: #e8e2db;"
      >
        {{ yongSin.yong_sin_label }}
      </span>
      <!-- 추론 우선순위 -->
      <span
        v-if="yongSin.reasoning_priority"
        class="px-2.5 py-1 text-xs rounded-full border"
        style="background: #f0ece8; color: #aaaaaa; border-color: #e8e2db;"
      >
        {{ yongSin.reasoning_priority }}
      </span>
    </div>
  </div>
</template>
