<script setup lang="ts">
import { computed } from 'vue'
import type { DayMasterStrength } from '~/types/saju'

const props = defineProps<{ strength: DayMasterStrength }>()

const LEVELS = ['극약', '태약', '신약', '중화신약', '중화신강', '신강', '태강', '극왕']
const LEVEL_IDX: Record<string, number> = Object.fromEntries(LEVELS.map((l, i) => [l, i]))
const DIST = [5, 12, 17, 19, 24, 6, 1, 1]
const DIST_TOTAL = DIST.reduce((a, b) => a + b, 0)

const ML = 32; const MB = 36; const MT = 14
const SVG_W = 320; const SVG_H = 180
const plotW = SVG_W - ML - 10
const plotH = SVG_H - MB - MT
const MAX_DIST = 25

const pts = computed(() =>
  DIST.map((d, i) => ({
    x: ML + (plotW / 7) * i,
    y: MT + plotH - (d / MAX_DIST) * plotH,
  }))
)

const polyline = computed(() =>
  pts.value.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
)

const areaPolygon = computed(() => {
  const base = MT + plotH
  const f = pts.value[0], l = pts.value[pts.value.length - 1]
  return `${f.x.toFixed(1)},${base} ${polyline.value} ${l.x.toFixed(1)},${base}`
})

const levelIdx = computed(() => LEVEL_IDX[props.strength.level_8] ?? 4)
const userPt   = computed(() => pts.value[levelIdx.value])
const userPct  = computed(() => (DIST[levelIdx.value] / DIST_TOTAL * 100).toFixed(1))

const deukList = [
  { key: 'deuk_ryeong' as const, label: '득령' },
  { key: 'deuk_ji'     as const, label: '득지' },
  { key: 'deuk_si'     as const, label: '득시' },
  { key: 'deuk_se'     as const, label: '득세' },
]

const yTicks = [0, 10, 20]
</script>

<template>
  <div class="card space-y-3">
    <h3 class="label-section">신강/신약지수</h3>

    <!-- 득령/득지/득시/득세 -->
    <div class="flex flex-wrap gap-4">
      <span v-for="d in deukList" :key="d.key" class="flex items-center gap-1">
        <span class="fs-label" style="color: var(--text-secondary);">{{ d.label }}</span>
        <svg v-if="strength[d.key]" width="18" height="18" viewBox="0 0 18 18">
          <circle cx="9" cy="9" r="8" fill="#2878c8" fill-opacity="0.12" stroke="#2878c8" stroke-width="1.5"/>
          <path d="M5.5 9l2.5 2.5 4-4" stroke="#2878c8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
        <svg v-else width="18" height="18" viewBox="0 0 18 18">
          <circle cx="9" cy="9" r="8" fill="#d43f3f" fill-opacity="0.10" stroke="#d43f3f" stroke-width="1.5"/>
          <path d="M6 6l6 6M12 6l-6 6" stroke="#d43f3f" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </span>
    </div>

    <p class="fs-body" style="color: var(--text-primary);">
      <strong>{{ strength.level_8 }}</strong>한 사주입니다.
    </p>
    <p class="fs-label" style="color: var(--text-muted);">
      {{ userPct }}%의 사람이 여기에 해당합니다.
    </p>

    <!-- 차트 -->
    <svg :viewBox="`0 0 ${SVG_W} ${SVG_H}`" class="w-full" xmlns="http://www.w3.org/2000/svg">
      <!-- 유저 위치 강조 컬럼 -->
      <rect
        :x="userPt.x - (plotW / 7) / 2" :y="MT"
        :width="plotW / 7" :height="plotH"
        fill="#f0ece8" opacity="0.9"
      />
      <!-- Y grid -->
      <g v-for="tick in yTicks" :key="tick">
        <line
          :x1="ML" :y1="MT + plotH - (tick / MAX_DIST) * plotH"
          :x2="SVG_W - 10" :y2="MT + plotH - (tick / MAX_DIST) * plotH"
          stroke="#e8e2db" stroke-width="1"
        />
        <text :x="ML - 4" :y="MT + plotH - (tick / MAX_DIST) * plotH + 4"
          text-anchor="end" font-size="9" fill="#aaaaaa">{{ tick }}</text>
      </g>
      <text :x="ML - 4" :y="SVG_H - 2" text-anchor="end" font-size="8" fill="#aaaaaa">(만명)</text>

      <!-- 면적 -->
      <polygon :points="areaPolygon" fill="#e0dbd4" opacity="0.5"/>
      <!-- 라인 -->
      <polyline :points="polyline" fill="none" stroke="#888888" stroke-width="1.8"
        stroke-linejoin="round" stroke-linecap="round"/>
      <!-- 일반 점 -->
      <circle v-for="(pt, i) in pts" :key="i"
        :cx="pt.x" :cy="pt.y" r="3" fill="white" stroke="#bbbbbb" stroke-width="1.2"/>
      <!-- 유저 점 -->
      <circle :cx="userPt.x" :cy="userPt.y" r="5" fill="#2a2a2a" stroke="white" stroke-width="1.5"/>
      <text :x="userPt.x" :y="userPt.y - 9"
        text-anchor="middle" font-size="11" fill="#2a2a2a" font-weight="700">나</text>
      <!-- X축 -->
      <text v-for="(label, i) in LEVELS" :key="label"
        :x="ML + (plotW / 7) * i" :y="SVG_H - 4"
        text-anchor="middle" font-size="9"
        :fill="i === levelIdx ? '#2a2a2a' : '#aaaaaa'"
        :font-weight="i === levelIdx ? '700' : '400'"
      >{{ label }}</text>
    </svg>
  </div>
</template>
