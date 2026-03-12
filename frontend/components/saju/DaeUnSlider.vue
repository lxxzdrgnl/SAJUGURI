<script setup lang="ts">
import type { DaeUnEntry } from '~/types/saju'

const props = defineProps<{
  daeUnList: DaeUnEntry[]
  currentDaeUn: DaeUnEntry
  startAge: number
}>()

// 오행 → 타일 배경색 (utils/elementColor.ts auto-import)
function bg(el: string) { return elColor(el) }

function isCurrent(entry: DaeUnEntry) {
  return entry.start_age === props.currentDaeUn?.start_age
}
</script>

<template>
  <div class="card space-y-3">
    <div class="flex items-center gap-2">
      <h3 class="label-section">대운 (大運)</h3>
      <span class="daeun-start-badge">{{ startAge }}세 시작</span>
    </div>

    <div class="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
      <div
        v-for="entry in daeUnList"
        :key="entry.start_age"
        class="flex-shrink-0 flex flex-col items-center gap-1"
      >
        <!-- 나이 + 천간 십성 -->
        <div class="flex flex-col items-center gap-0.5">
          <span class="fs-label font-semibold" style="color: var(--text-muted);">
            {{ entry.start_age }}세
          </span>
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
            class="font-bold leading-none"
            style="font-family: var(--font-ganji);"
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
            class="font-bold leading-none"
            style="font-family: var(--font-ganji);"
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
            현재
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.daeun-start-badge {
  font-size: var(--fs-label);
  font-weight: 600;
  color: var(--text-primary);
  background: var(--surface-3);
  border: 1px solid var(--border-subtle);
  border-radius: 999px;
  padding: 2px 10px;
}

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
