<script setup lang="ts">
import type { YeonUnEntry } from '~/types/saju'

const props = defineProps<{
  dayStem: string
}>()

const { getYeonUn } = useSajuApi()

const currentYear = new Date().getFullYear()
const startYear = currentYear - 4

const { data: yeonUnList, pending, error } = await useAsyncData(
  `yeon-un-${startYear}-${props.dayStem}`,
  () => getYeonUn(startYear, 12, props.dayStem),
  { default: () => [] as YeonUnEntry[] }
)

// 오행 → 타일 배경색 (utils/elementColor.ts auto-import)
function bg(el: string) { return elColor(el) }

function isCurrent(entry: YeonUnEntry) { return entry.year === currentYear }
function isPast(entry: YeonUnEntry)    { return entry.year < currentYear }
</script>

<template>
  <div class="card space-y-3">
    <h3 class="label-section">연운 (年運)</h3>

    <div v-if="pending" class="flex items-center gap-2 text-sm py-2" style="color: var(--text-muted);">
      <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
      연운 불러오는 중...
    </div>
    <div v-else-if="error" class="text-sm py-2" style="color: var(--color-bad);">연운 데이터를 불러올 수 없습니다.</div>

    <div v-else class="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
      <div
        v-for="entry in (yeonUnList ?? [])"
        :key="entry.year"
        class="flex-shrink-0 flex flex-col items-center gap-1"
        :style="isPast(entry) ? 'opacity: 0.5;' : ''"
      >
        <!-- 연도 + 천간 십성 -->
        <div class="flex flex-col items-center gap-0.5">
          <span class="fs-label font-semibold" style="color: var(--text-muted);">{{ entry.year }}</span>
          <span v-if="entry.stem_ten_god" class="fs-label" style="color: var(--text-muted);">
            {{ entry.stem_ten_god }}
          </span>
        </div>

        <!-- 천간 타일 -->
        <div
          class="slider-tile flex items-center justify-center transition-all"
          :style="isCurrent(entry)
            ? `background: var(--surface-2); border: 2.5px solid var(--text-primary); box-shadow: 0 0 0 1px var(--text-primary);`
            : `background: ${bg(entry.stem_element)}; border: 2.5px solid transparent;`"
        >
          <span
            class="font-bold leading-none" style="font-family: var(--font-ganji);"
            :style="`font-size: var(--fs-tile); letter-spacing: 0.02em; ${isCurrent(entry) ? `color: ${bg(entry.stem_element)};` : 'color: rgba(255,255,255,0.95);'}`"
          >{{ entry.stem }}</span>
        </div>

        <!-- 지지 타일 -->
        <div
          class="slider-tile flex items-center justify-center transition-all"
          :style="isCurrent(entry)
            ? `background: var(--surface-2); border: 2.5px solid var(--text-primary); box-shadow: 0 0 0 1px var(--text-primary);`
            : `background: ${bg(entry.branch_element)}; border: 2.5px solid transparent;`"
        >
          <span
            class="font-bold leading-none" style="font-family: var(--font-ganji);"
            :style="`font-size: var(--fs-tile); letter-spacing: 0.02em; ${isCurrent(entry) ? `color: ${bg(entry.branch_element)};` : 'color: rgba(255,255,255,0.95);'}`"
          >{{ entry.branch }}</span>
        </div>

        <!-- 지지 십성 + 12운성 -->
        <div class="flex flex-col items-center gap-0.5">
          <span v-if="entry.branch_ten_god" class="fs-label" style="color: var(--text-muted);">
            {{ entry.branch_ten_god }}
          </span>
          <span v-if="entry.twelve_wun" class="fs-label" style="color: var(--el-토);">
            {{ entry.twelve_wun }}
          </span>
          <span v-if="isCurrent(entry)" class="fs-label font-bold mt-0.5" style="color: var(--text-primary);">
            올해
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.slider-tile {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 12px;
}

@media (max-width: 480px) {
  .slider-tile {
    width: 2.75rem;
    height: 2.75rem;
    border-radius: 9px;
    --fs-tile: 1.5rem;
  }
}
</style>
