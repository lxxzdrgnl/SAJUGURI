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
    <div class="flex items-baseline gap-2">
      <h3 class="label-section">대운 (大運)</h3>
      <span class="text-xs" style="color: #aaaaaa;">{{ startAge }}세 시작</span>
    </div>

    <div class="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
      <div
        v-for="entry in daeUnList"
        :key="entry.start_age"
        class="flex-shrink-0 flex flex-col items-center gap-1"
      >
        <!-- 나이 + 천간 십성 -->
        <div class="flex flex-col items-center gap-0.5">
          <span class="fs-label font-semibold" style="color: #888888;">
            {{ entry.start_age }}세
          </span>
          <span v-if="entry.stem_ten_god" class="fs-label" style="color: #aaaaaa;">
            {{ entry.stem_ten_god }}
          </span>
        </div>

        <!-- 천간 타일 -->
        <div
          class="slider-tile flex items-center justify-center transition-all"
          :style="isCurrent(entry)
            ? `background: #f7f4f1; border: 2.5px solid #2a2a2a; box-shadow: 0 0 0 1px #2a2a2a;`
            : `background: ${bg(entry.stem_element)}; border: 2.5px solid transparent;`"
        >
          <span
            class="font-bold font-serif leading-none"
            :style="`font-size: var(--fs-tile); letter-spacing: 0.02em; ${isCurrent(entry) ? `color: ${bg(entry.stem_element)};` : 'color: rgba(255,255,255,0.95);'}`"
          >{{ entry.stem }}</span>
        </div>

        <!-- 지지 타일 -->
        <div
          class="slider-tile flex items-center justify-center transition-all"
          :style="isCurrent(entry)
            ? `background: #f7f4f1; border: 2.5px solid #2a2a2a; box-shadow: 0 0 0 1px #2a2a2a;`
            : `background: ${bg(entry.branch_element)}; border: 2.5px solid transparent;`"
        >
          <span
            class="font-bold font-serif leading-none"
            :style="`font-size: var(--fs-tile); letter-spacing: 0.02em; ${isCurrent(entry) ? `color: ${bg(entry.branch_element)};` : 'color: rgba(255,255,255,0.95);'}`"
          >{{ entry.branch }}</span>
        </div>

        <!-- 지지 십성 + 12운성 -->
        <div class="flex flex-col items-center gap-0.5">
          <span v-if="entry.branch_ten_god" class="fs-label" style="color: #aaaaaa;">
            {{ entry.branch_ten_god }}
          </span>
          <span v-if="entry.twelve_wun" class="fs-label" style="color: #a67c52;">
            {{ entry.twelve_wun }}
          </span>
          <span v-if="isCurrent(entry)" class="fs-label font-bold mt-0.5" style="color: #2a2a2a;">
            현재
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
