<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = defineProps<{
  data: Record<string, number>
  dayElement: string
}>()

// 오행 → 색상 (utils/elementColor.ts auto-import)
function ec(el: string) { return elColor(el) }

const cx = 150
const cy = 150
const baseRadius = 90

const elements = ['목', '화', '토', '금', '수']
const anglesDeg = [-90, -18, 54, 126, 198]

function toRad(deg: number) { return (deg * Math.PI) / 180 }

const vertices = computed(() =>
  anglesDeg.map((deg) => ({
    x: cx + baseRadius * Math.cos(toRad(deg)),
    y: cy + baseRadius * Math.sin(toRad(deg)),
  }))
)

const pentagonPoints = computed(() =>
  vertices.value.map((v) => `${v.x.toFixed(2)},${v.y.toFixed(2)}`).join(' ')
)

const sangSaengPairs = [[0,1],[1,2],[2,3],[3,4],[4,0]]
const sangGeukPairs  = [[0,2],[2,4],[4,1],[1,3],[3,0]]

function circleRadius(el: string) {
  const pct = props.data[el] ?? 0
  return Math.max(14, Math.min(32, 14 + (pct / 100) * 18))
}

function arrowPath(fromIdx: number, toIdx: number) {
  const from = vertices.value[fromIdx]
  const to   = vertices.value[toIdx]
  const dx = to.x - from.x, dy = to.y - from.y
  const dist = Math.sqrt(dx*dx + dy*dy)
  const rFrom = circleRadius(elements[fromIdx])
  const rTo   = circleRadius(elements[toIdx])
  const ux = dx/dist, uy = dy/dist
  return `M${(from.x + ux*(rFrom+3)).toFixed(2)},${(from.y + uy*(rFrom+3)).toFixed(2)} L${(to.x - ux*(rTo+6)).toFixed(2)},${(to.y - uy*(rTo+6)).toFixed(2)}`
}

function linePath(fromIdx: number, toIdx: number) {
  const from = vertices.value[fromIdx], to = vertices.value[toIdx]
  return `M${from.x.toFixed(2)},${from.y.toFixed(2)} L${to.x.toFixed(2)},${to.y.toFixed(2)}`
}

// % 레이블 위치: 원 바깥쪽
function pctLabelPos(i: number) {
  const v = vertices.value[i]
  const dx = v.x - cx, dy = v.y - cy
  const dist = Math.sqrt(dx*dx + dy*dy)
  const offset = circleRadius(elements[i]) + 14
  return {
    x: v.x + (dx/dist) * offset,
    y: v.y + (dy/dist) * offset + 4,
  }
}

</script>

<template>
  <div class="card flex flex-col items-center">
    <h3 class="label-section mb-4 self-start">오행 오각형</h3>
    <svg viewBox="0 0 300 300" class="w-full max-w-[300px]" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrow-teal" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
          <path d="M0,0 L0,6 L8,3 z" fill="#3a90a8" opacity="0.7"/>
        </marker>
      </defs>

      <!-- 오각형 아웃라인 -->
      <polygon :points="pentagonPoints" fill="none" stroke="#ddd7d0"
        stroke-width="1" stroke-dasharray="4,3" opacity="0.8"/>

      <!-- 상극 점선 -->
      <path v-for="([fi, ti], idx) in sangGeukPairs" :key="`geuk-${idx}`"
        :d="linePath(fi, ti)" stroke="#c8503c" stroke-width="1"
        stroke-dasharray="4,3" opacity="0.2" fill="none"/>

      <!-- 상생 화살표 -->
      <path v-for="([fi, ti], idx) in sangSaengPairs" :key="`saeng-${idx}`"
        :d="arrowPath(fi, ti)" stroke="#3a90a8" stroke-width="1.5"
        opacity="0.45" fill="none" marker-end="url(#arrow-teal)"/>

      <!-- 중앙 일간 -->
      <circle cx="150" cy="150" r="24" fill="#f7f4f1" stroke="#ddd7d0" stroke-width="1.5"/>
      <text x="150" y="146" text-anchor="middle" font-size="10" fill="#aaaaaa" font-family="sans-serif">일간</text>
      <text x="150" y="162" text-anchor="middle" font-size="15" font-weight="bold"
        :fill="ec(dayElement)" font-family="sans-serif">{{ dayElement }}</text>

      <!-- 꼭짓점 노드 -->
      <g v-for="(el, i) in elements" :key="el" class="element-node">
        <!-- 메인 원 -->
        <circle
          :cx="vertices[i].x" :cy="vertices[i].y"
          :r="circleRadius(el)"
          :fill="ec(el)" fill-opacity="0.12"
          :stroke="ec(el)" stroke-width="1.5"
        />
        <!-- 오행 문자 -->
        <text
          :x="vertices[i].x" :y="vertices[i].y + 6"
          text-anchor="middle" font-size="16" font-weight="bold"
          :fill="ec(el)" font-family="sans-serif"
        >{{ el }}</text>
        <!-- % 레이블 -->
        <text
          :x="pctLabelPos(i).x" :y="pctLabelPos(i).y"
          text-anchor="middle" font-size="13" font-weight="600"
          :fill="ec(el)" font-family="sans-serif" opacity="0.9"
        >{{ data[el] ?? 0 }}%</text>
      </g>
    </svg>

    <!-- 범례 -->
    <div class="flex gap-5 mt-2 fs-label" style="color: var(--text-muted);">
      <span class="flex items-center gap-1.5">
        <span class="w-5 h-0.5 inline-block" style="background: var(--el-목);"/>
        상생
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-5 h-0.5 inline-block" style="border-top: 1.5px dashed var(--el-화); background: transparent;"/>
        상극
      </span>
    </div>
  </div>
</template>

<style scoped>
/* 원 부드러운 전환 */
.element-node circle {
  transition: r 0.4s ease, fill-opacity 0.3s ease;
}
</style>
