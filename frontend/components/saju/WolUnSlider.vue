<script setup lang="ts">
import type { WolUnEntry } from '~/types/saju'

const props = defineProps<{
  year: number
  dayStem: string
}>()

const { getWolUn } = useSajuApi()

const currentMonth = new Date().getMonth() + 1

const { data: wolUnList, pending, error } = await useAsyncData(
  `wol-un-${props.year}-${props.dayStem}`,
  () => getWolUn(props.year, props.dayStem),
  { default: () => [] as WolUnEntry[] }
)

// 오행 → 타일 배경색 (utils/elementColor.ts auto-import)
function bg(el: string) { return elColor(el) }

const monthNames = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']

function isCurrent(entry: WolUnEntry) { return entry.month === currentMonth }
</script>

<template>
  <div class="card space-y-3">
    <div class="flex items-baseline gap-2">
      <h3 class="label-section">월운 (月運)</h3>
      <span class="text-xs" style="color: #aaaaaa;">{{ year }}년</span>
    </div>

    <div v-if="pending" class="flex items-center gap-2 text-sm py-2" style="color: #aaaaaa;">
      <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
      월운 불러오는 중...
    </div>
    <div v-else-if="error" class="text-sm py-2" style="color: #d43f3f;">월운 데이터를 불러올 수 없습니다.</div>

    <div v-else class="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
      <div
        v-for="entry in (wolUnList ?? [])"
        :key="entry.month"
        class="flex-shrink-0 flex flex-col items-center gap-1"
      >
        <!-- 월 + 천간 십성 -->
        <div class="flex flex-col items-center gap-0.5">
          <span class="fs-label font-semibold" style="color: #888888;">
            {{ monthNames[entry.month - 1] }}
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
            이번달
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
