<script setup lang="ts">
import type { YongSin } from '~/types/saju'

const props = defineProps<{
  yongSin: YongSin
  wuxingPct?: Record<string, number>   // 현재 오행 비율 (작동도 계산용)
}>()

// 용신 작동도: 용신 오행 비율 기준 (이상: 20%, 과다면 이미 충족, 부족하면 낮음)
const activation = computed(() => {
  const pct = props.wuxingPct?.[props.yongSin.primary] ?? null
  if (pct === null) return null
  if (pct < 10) return { label: '낮음', desc: `${props.yongSin.primary} ${pct}% — 매우 부족`, color: 'var(--color-bad)' }
  if (pct < 18) return { label: '보통', desc: `${props.yongSin.primary} ${pct}% — 약간 부족`, color: 'var(--el-토)' }
  return { label: '양호', desc: `${props.yongSin.primary} ${pct}% — 충분히 존재`, color: 'var(--color-good)' }
})

// 오행 → 색상 (utils/elementColor.ts auto-import)
function dotColor(el: string) { return elColor(el) }
</script>

<template>
  <div class="card space-y-4">
    <div class="flex items-center gap-1.5">
      <h3 class="label-section">용신 · 희신 · 기신 (用神)</h3>
      <UiInfoTooltip text="사주의 균형을 맞추는 핵심 오행입니다. 용신은 가장 필요한 기운, 희신은 용신을 돕는 기운, 기신은 균형을 해치는 기운입니다." />
    </div>

    <!-- 용신 (primary) -->
    <div class="flex items-center gap-3">
      <span class="text-xs w-10 shrink-0" style="color: var(--text-muted);">용신</span>
      <div
        class="flex items-center gap-2 px-4 py-2 rounded-lg border"
        style="background: rgba(40,120,200,0.06); border-color: rgba(40,120,200,0.2);"
      >
        <span
          class="w-3 h-3 rounded-full shrink-0"
          :style="{ backgroundColor: dotColor(yongSin.primary) }"
        />
        <span class="text-base font-bold" style="color: var(--text-primary);">{{ yongSin.primary }}</span>
      </div>
      <div
        v-if="yongSin.secondary"
        class="flex items-center gap-2 px-3 py-2 rounded-lg border"
        style="background: var(--surface-2); border-color: var(--border-subtle);"
      >
        <span
          class="w-2.5 h-2.5 rounded-full shrink-0"
          :style="{ backgroundColor: dotColor(yongSin.secondary) }"
        />
        <span class="text-sm" style="color: var(--text-secondary);">{{ yongSin.secondary }}</span>
      </div>
    </div>

    <!-- 희신 (xi_sin) -->
    <div v-if="yongSin.xi_sin?.length" class="flex items-center gap-3">
      <span class="text-xs w-10 shrink-0" style="color: var(--text-muted);">희신</span>
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
      <span class="text-xs w-10 shrink-0" style="color: var(--text-muted);">기신</span>
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
    <div class="pt-3 space-y-2" style="border-top: 1px solid var(--surface-3);">
      <div class="flex flex-wrap gap-2">
        <!-- 용신 레이블 -->
        <span
          v-if="yongSin.yong_sin_label"
          class="px-2.5 py-1 text-xs rounded-full border"
          style="background: var(--surface-3); color: var(--text-muted); border-color: var(--border-subtle);"
        >
          {{ yongSin.yong_sin_label }}
        </span>
        <!-- 추론 우선순위 -->
        <span
          v-if="yongSin.reasoning_priority"
          class="px-2.5 py-1 text-xs rounded-full border"
          style="background: var(--surface-3); color: var(--text-muted); border-color: var(--border-subtle);"
        >
          {{ yongSin.reasoning_priority }}
        </span>
      </div>
      <!-- 용신 작동도 -->
      <div v-if="activation" class="flex items-center gap-2 fs-tiny">
        <span style="color: var(--text-muted);">용신 활성도</span>
        <span
          class="px-2 py-0.5 rounded border font-semibold"
          :style="`color: ${activation.color}; background: color-mix(in srgb, ${activation.color} 10%, transparent); border-color: color-mix(in srgb, ${activation.color} 25%, transparent);`"
        >{{ activation.label }}</span>
        <span style="color: var(--text-muted);">{{ activation.desc }}</span>
      </div>
    </div>
  </div>
</template>
