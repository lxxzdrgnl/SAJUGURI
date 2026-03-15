<script setup lang="ts">
import { computed, toRaw, markRaw } from 'vue'
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

// 오행 색상 (utils/elementColor.ts EL_HEX — Chart.js는 CSS var 미지원)
const elementColors = EL_HEX

const elementOrder = ['목', '화', '토', '금', '수']

const chartData = computed(() => {
  const d = toRaw(props.data)
  const labels: string[] = []
  const values: number[] = []
  const colors: string[] = []

  for (const el of elementOrder) {
    const val = d[el] ?? 0
    if (val > 0) {
      labels.push(`${el} ${val}%`)
      values.push(val)
      colors.push(elementColors[el] ?? '#888')
    }
  }

  return {
    labels,
    datasets: [{
      data: values,
      backgroundColor: colors,
      borderColor: '#ffffff',
      borderWidth: 3,
      hoverBorderColor: '#f4f2ef',
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
      onClick: () => {},
      labels: {
        color: '#5a5450',
        font: { size: 14, family: 'Joseon100Years' },
        padding: 14,
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
  <div class="flex flex-col items-center">
    <ClientOnly>
      <div class="w-full max-w-[200px]">
        <Doughnut :data="chartData" :options="chartOptions" />
      </div>
      <template #fallback>
        <div class="h-48 flex items-center justify-center fs-label" style="color: var(--text-muted);">차트 로딩 중...</div>
      </template>
    </ClientOnly>
  </div>
</template>
