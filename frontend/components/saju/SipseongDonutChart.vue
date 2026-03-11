<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  data: Record<string, number>
}>()

// 십성 → 오행 매핑 → EL_HEX 색상 (utils/elementColor.ts)
// 편/정은 같은 오행이므로 밝기로 구분
const TG_ELEMENT: Record<string, string> = {
  '비견': '목', '겁재': '목',
  '식신': '화', '상관': '화',
  '편재': '토', '정재': '토',
  '편관': '금', '정관': '금',
  '편인': '수', '정인': '수',
}
function sipseongColor(ss: string, isPyeon: boolean): string {
  const hex = EL_HEX[TG_ELEMENT[ss] ?? ''] ?? '#888888'
  // 편(偏)은 원색, 정(正)은 약간 밝게
  if (!isPyeon) return hex + 'cc'
  return hex
}
const sipseongColors: Record<string, string> = Object.fromEntries(
  Object.keys(TG_ELEMENT).map(ss => [ss, sipseongColor(ss, ss.startsWith('편') || ss === '비견' || ss === '겁재')])
)

const sipseongOrder = ['비견', '겁재', '식신', '상관', '편재', '정재', '편관', '정관', '편인', '정인']

const chartData = computed(() => {
  const labels: string[] = []
  const values: number[] = []
  const colors: string[] = []

  for (const ss of sipseongOrder) {
    const val = props.data[ss] ?? 0
    if (val > 0) {
      labels.push(`${ss} ${val}%`)
      values.push(val)
      colors.push(sipseongColors[ss] ?? '#888')
    }
  }

  return {
    labels,
    datasets: [{
      data: values,
      backgroundColor: colors,
      borderColor: '#ffffff',
      borderWidth: 3,
      hoverBorderColor: '#f7f4f1',
    }],
  }
})

const chartOptions = {
  cutout: '65%',
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        color: '#666666',
        font: { size: 13 },
        padding: 12,
        boxWidth: 12,
        boxHeight: 12,
      },
    },
    tooltip: {
      callbacks: {
        label: (ctx: { label?: string; parsed?: number }) => {
          return ` ${ctx.parsed ?? 0}%`
        },
      },
    },
  },
}
</script>

<template>
  <div class="card flex flex-col items-center">
    <h3 class="label-section mb-4 self-start">십성 분포</h3>
    <ClientOnly>
      <div class="w-full max-w-[240px]">
        <Doughnut :data="chartData" :options="chartOptions" />
      </div>
      <template #fallback>
        <div class="h-48 flex items-center justify-center text-sm" style="color: #aaaaaa;">차트 로딩 중...</div>
      </template>
    </ClientOnly>
  </div>
</template>
