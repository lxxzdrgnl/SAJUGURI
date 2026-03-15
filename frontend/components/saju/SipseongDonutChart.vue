<script setup lang="ts">
import { computed, toRaw, ref } from 'vue'
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

// 십성 그룹 (비겁/식상/재성/관성/인성)
const TG_GROUP: Record<string, string> = {
  '비견': '비겁', '겁재': '비겁',
  '식신': '식상', '상관': '식상',
  '편재': '재성', '정재': '재성',
  '편관': '관성', '정관': '관성',
  '편인': '인성', '정인': '인성',
}
// 십성 개별 설명
const TG_DESC: Record<string, string> = {
  '비견': '나와 같은 오행·음양. 독립심·경쟁심이 강함',
  '겁재': '나와 같은 오행·다른 음양. 추진력·승부욕이 강함',
  '식신': '내가 생하는 같은 음양. 표현력·복록·예술적 감각',
  '상관': '내가 생하는 다른 음양. 창의성·언변·관성 극제',
  '편재': '내가 극하는 같은 음양. 현실 감각·사업·이성 인연',
  '정재': '내가 극하는 다른 음양. 성실·근검·안정적 재물',
  '편관': '나를 극하는 같은 음양. 통솔력·도전·칠살(七殺)',
  '정관': '나를 극하는 다른 음양. 명예·규범·안정적 직위',
  '편인': '나를 생하는 같은 음양. 직관·전문성·종교·예술',
  '정인': '나를 생하는 다른 음양. 학문·자비·모성·지식',
}

const GROUP_LABEL: Record<string, string> = {
  '비겁': '자아·독립', '식상': '표현·창의',
  '재성': '재물·현실', '관성': '명예·규범', '인성': '학문·보호',
}
const GROUP_ORDER = ['비겁', '식상', '재성', '관성', '인성']

const groupSummary = computed(() => {
  const d = toRaw(props.data)
  const groups: Record<string, number> = {}
  for (const [ss, pct] of Object.entries(d)) {
    const g = TG_GROUP[ss]
    if (g) groups[g] = (groups[g] ?? 0) + pct
  }
  return GROUP_ORDER
    .filter(g => (groups[g] ?? 0) > 0)
    .map(g => ({ group: g, label: GROUP_LABEL[g], pct: groups[g] ?? 0 }))
    .sort((a, b) => b.pct - a.pct)
})

const dominantGroups = computed(() => groupSummary.value.slice(0, 2).map(g => g.group))

const chartData = computed(() => {
  const d = toRaw(props.data)
  const labels: string[] = []
  const values: number[] = []
  const colors: string[] = []

  for (const ss of sipseongOrder) {
    const val = d[ss] ?? 0
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
        font: { size: 13, family: 'Joseon100Years' },
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
        afterLabel: (ctx: { label?: string }) => {
          const name = (ctx.label ?? '').split(' ')[0]
          return TG_DESC[name] ? `  ${TG_DESC[name]}` : ''
        },
      },
    },
  },
}
</script>

<template>
  <div class="card flex flex-col items-center">
    <div class="flex items-center gap-1.5 mb-4 self-start">
      <h3 class="label-section">십성 분포</h3>
      <UiInfoTooltip text="사주 여덟 글자의 십성(十星) 비율입니다. 비겁(자아)·식상(표현)·재성(재물)·관성(명예)·인성(학문) 다섯 그룹으로 나뉘며, 어떤 그룹이 강한지에 따라 성격과 삶의 방식이 달라집니다." />
    </div>
    <ClientOnly>
      <div class="w-full max-w-[240px]">
        <Doughnut :data="chartData" :options="chartOptions" />
      </div>
      <template #fallback>
        <div class="h-48 flex items-center justify-center text-sm" style="color: var(--text-muted);">차트 로딩 중...</div>
      </template>
    </ClientOnly>

    <!-- 그룹 요약 -->
    <div v-if="groupSummary.length" class="w-full mt-3 space-y-1.5" style="border-top: 1px solid var(--surface-3); padding-top: 10px;">
      <p class="fs-tiny font-semibold tracking-wide" style="color: var(--text-muted);">십성 구조 요약</p>
      <div v-for="g in groupSummary" :key="g.group" class="flex items-center gap-2">
        <div class="flex-1 flex items-center gap-1.5">
          <div class="w-[72px] shrink-0">
            <span
              class="fs-label font-bold block"
              :style="dominantGroups.includes(g.group) ? 'color: var(--accent);' : 'color: var(--text-secondary);'"
            >{{ g.group }}</span>
            <span class="fs-tiny" style="color: var(--text-muted);">{{ GROUP_LABEL[g.group] }}</span>
          </div>
          <div class="flex-1 h-1.5 rounded-full overflow-hidden" style="background: var(--surface-3);">
            <div
              class="h-full rounded-full transition-all duration-500"
              :style="`width: ${g.pct}%; background: ${dominantGroups.includes(g.group) ? 'var(--accent)' : 'var(--border-default)'};`"
            />
          </div>
          <span class="fs-label w-8 text-right shrink-0" style="color: var(--text-muted);">{{ g.pct }}%</span>
        </div>
      </div>
      <p v-if="dominantGroups.length" class="fs-tiny" style="color: var(--text-muted);">
        핵심 구조: <strong style="color: var(--text-secondary);">{{ dominantGroups.join(' + ') }}</strong>
      </p>
    </div>
  </div>
</template>
