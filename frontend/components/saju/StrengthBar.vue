<script setup lang="ts">
import type { DayMasterStrength } from '~/types/saju'

const props = defineProps<{
  strength: DayMasterStrength
}>()

const segments = [
  { key: '극약',    label: '극약' },
  { key: '태약',    label: '태약' },
  { key: '신약',    label: '신약' },
  { key: '중화신약', label: '중화신약' },
  { key: '중화신강', label: '중화신강' },
  { key: '신강',    label: '신강' },
  { key: '태강',    label: '태강' },
  { key: '극왕',    label: '극왕' },
]

const deukItems = [
  { label: '득령', key: 'deuk_ryeong' as const },
  { label: '득지', key: 'deuk_ji' as const },
  { label: '득시', key: 'deuk_si' as const },
  { label: '득세', key: 'deuk_se' as const },
]
</script>

<template>
  <div class="card space-y-4">
    <h3 class="label-section">일간 강약 (日干强弱)</h3>

    <!-- 현재 레벨 강조 표시 -->
    <div class="text-center py-2">
      <span class="text-lg font-bold" style="color: #3a3a3a;">{{ strength.level_8 }}</span>
      <span class="ml-2 text-sm" style="color: #aaaaaa;">({{ strength.score }}점)</span>
    </div>

    <!-- 8단계 바 -->
    <div class="flex rounded-lg overflow-hidden" style="border: 1px solid #e8e2db;">
      <div
        v-for="seg in segments"
        :key="seg.key"
        class="flex-1 py-2 text-center transition-all"
        :style="
          seg.key === strength.level_8
            ? 'background: #3a3a3a; color: #ffffff; font-weight: 700; font-size: 11px;'
            : 'background: #f7f4f1; color: #bbbbbb; font-size: 10px;'
        "
      >
        <span class="hidden sm:block">{{ seg.label }}</span>
        <span class="sm:hidden">{{ seg.label.slice(0, 2) }}</span>
      </div>
    </div>

    <!-- 점수 바 -->
    <div class="space-y-1">
      <div class="flex justify-between text-[11px]" style="color: #aaaaaa;">
        <span>약 (0)</span>
        <span>중화 (50)</span>
        <span>강 (100)</span>
      </div>
      <div class="relative h-2.5 rounded-full overflow-hidden" style="background: #f0ece8;">
        <!-- 현재 점수 마커 -->
        <div
          class="absolute top-0 h-full w-1 rounded-full transition-all duration-500"
          style="background: #3a3a3a;"
          :style="{ left: `${Math.max(0, Math.min(100, strength.score))}%`, transform: 'translateX(-50%)' }"
        />
        <!-- 채워진 바 -->
        <div
          class="h-full rounded-full transition-all duration-500"
          style="background: rgba(58,58,58,0.3);"
          :style="{ width: `${Math.max(0, Math.min(100, strength.score))}%` }"
        />
      </div>
    </div>

    <!-- 득령/득지/득시/득세 뱃지 -->
    <div class="flex justify-around pt-1" style="border-top: 1px solid #f0ece8;">
      <div
        v-for="item in deukItems"
        :key="item.key"
        class="flex flex-col items-center gap-1"
      >
        <span class="text-xs" style="color: #aaaaaa;">{{ item.label }}</span>
        <span
          class="text-xl font-bold leading-none"
          :style="strength[item.key] ? 'color: #2878c8;' : 'color: #e8e2db;'"
        >
          {{ strength[item.key] ? '○' : '✗' }}
        </span>
      </div>
    </div>
  </div>
</template>
