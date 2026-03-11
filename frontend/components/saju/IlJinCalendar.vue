<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { IlJinEntry } from '~/types/saju'

const { getIlJin } = useSajuApi()

const today = new Date()
const year = ref(today.getFullYear())
const month = ref(today.getMonth() + 1)
const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

const ilJinData = ref<IlJinEntry[]>([])
const pending = ref(false)
const fetchError = ref<string | null>(null)

async function fetchData() {
  pending.value = true
  fetchError.value = null
  try {
    ilJinData.value = await getIlJin(year.value, month.value)
  } catch {
    fetchError.value = '일진 데이터를 불러올 수 없습니다.'
    ilJinData.value = []
  } finally {
    pending.value = false
  }
}

watch([year, month], fetchData, { immediate: true })

const weekdays = ['일', '월', '화', '수', '목', '금', '토']
const monthNames = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']

// 일진 맵 { 'YYYY-MM-DD': IlJinEntry }
const ilJinMap = computed(() => {
  const map: Record<string, IlJinEntry> = {}
  for (const entry of ilJinData.value) {
    map[entry.date] = entry
  }
  return map
})

// 해당 월의 달력 그리드 생성
const calendarGrid = computed(() => {
  const firstDay = new Date(year.value, month.value - 1, 1)
  const daysInMonth = new Date(year.value, month.value, 0).getDate()
  const startWeekday = firstDay.getDay() // 0=일 ~ 6=토

  const cells: Array<{ date: string | null; day: number | null; entry: IlJinEntry | null }> = []

  // 앞 빈칸
  for (let i = 0; i < startWeekday; i++) {
    cells.push({ date: null, day: null, entry: null })
  }

  // 날짜 채우기
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year.value}-${String(month.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    cells.push({
      date: dateStr,
      day: d,
      entry: ilJinMap.value[dateStr] ?? null,
    })
  }

  // 뒤 빈칸 (6행 완성)
  while (cells.length % 7 !== 0) {
    cells.push({ date: null, day: null, entry: null })
  }

  return cells
})

function prevMonth() {
  if (month.value === 1) { year.value--; month.value = 12 }
  else { month.value-- }
}

function nextMonth() {
  if (month.value === 12) { year.value++; month.value = 1 }
  else { month.value++ }
}

function isToday(dateStr: string | null) {
  return dateStr === todayStr
}

function isSunday(idx: number) {
  return idx % 7 === 0
}

function isSaturday(idx: number) {
  return idx % 7 === 6
}
</script>

<template>
  <div class="card space-y-4">
    <!-- 헤더 -->
    <div class="flex items-center justify-between">
      <h3 class="label-section">일진 달력 (日辰)</h3>
      <div class="flex items-center gap-3">
        <button
          class="p-1.5 rounded-lg transition-colors"
          style="color: #888888;"
          @mouseenter="($event.target as HTMLElement).style.background = '#f0ece8'"
          @mouseleave="($event.target as HTMLElement).style.background = 'transparent'"
          @click="prevMonth"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <span class="fs-body font-medium min-w-[80px] text-center" style="color: #1a1a1a;">
          {{ year }}년 {{ monthNames[month - 1] }}
        </span>
        <button
          class="p-1.5 rounded-lg transition-colors"
          style="color: #888888;"
          @mouseenter="($event.target as HTMLElement).style.background = '#f0ece8'"
          @mouseleave="($event.target as HTMLElement).style.background = 'transparent'"
          @click="nextMonth"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="pending" class="flex items-center justify-center gap-2 text-sm py-8" style="color: #aaaaaa;">
      <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
      일진 불러오는 중...
    </div>

    <!-- 에러 -->
    <div v-else-if="fetchError" class="text-sm text-center py-4" style="color: #d43f3f;">
      {{ fetchError }}
    </div>

    <!-- 달력 -->
    <template v-else>
      <!-- 요일 헤더 -->
      <div class="grid grid-cols-7 gap-1">
        <div
          v-for="(wd, i) in weekdays"
          :key="wd"
          class="text-center fs-sub font-medium py-2"
          :style="i === 0 ? `color: var(--el-화);` : i === 6 ? `color: var(--el-수);` : 'color: #aaaaaa;'"
        >
          {{ wd }}
        </div>
      </div>

      <!-- 날짜 그리드 -->
      <div class="grid grid-cols-7 gap-1">
        <div
          v-for="(cell, idx) in calendarGrid"
          :key="idx"
          class="relative min-h-[80px] rounded-lg p-1.5 transition-all"
          :style="[
            cell.date ? 'cursor: default;' : '',
            isToday(cell.date) ? 'box-shadow: 0 0 0 2px #3a3a3a; background: #f7f4f1;' : '',
            !isToday(cell.date) && cell.entry?.solar_term ? 'background: rgba(166,124,82,0.06);' : '',
            !isToday(cell.date) && cell.date && !cell.entry?.solar_term ? '' : '',
          ].filter(Boolean).join(' ')"
        >
          <template v-if="cell.day">
            <!-- 날짜 숫자 -->
            <div
              class="fs-sub font-medium mb-0.5"
              :style="[
                isToday(cell.date) ? 'color: #3a3a3a; font-weight: 700;' : '',
                !isToday(cell.date) && isSunday(idx) ? 'color: #d43f3f;' : '',
                !isToday(cell.date) && isSaturday(idx) ? 'color: #2878c8;' : '',
                !isToday(cell.date) && !isSunday(idx) && !isSaturday(idx) ? 'color: #1a1a1a;' : '',
              ].filter(Boolean).join(' ')"
            >
              {{ cell.day }}
            </div>

            <!-- 절기 표시 -->
            <div
              v-if="cell.entry?.solar_term"
              class="fs-label font-medium leading-tight mb-0.5"
              style="color: #a67c52;"
            >
              {{ cell.entry.solar_term }}
            </div>

            <!-- 간지 -->
            <div
              v-if="cell.entry"
              class="fs-label leading-tight font-medium"
              style="color: #666666;"
            >
              {{ cell.entry.ganji_name }}
            </div>

            <!-- 음력 날짜 -->
            <div
              v-if="cell.entry"
              class="fs-label leading-tight mt-0.5"
              :style="cell.entry.is_leap_month ? 'color: #2878c8;' : 'color: #aaaaaa;'"
            >
              {{ cell.entry.is_leap_month ? '(윤)' : '' }}{{ cell.entry.lunar_month }}/{{ cell.entry.lunar_day }}
            </div>
          </template>
        </div>
      </div>

      <!-- 범례 -->
      <div class="flex flex-wrap gap-4 pt-2 fs-label" style="border-top: 1px solid #f0ece8; color: #aaaaaa;">
        <span class="flex items-center gap-1.5">
          <span
            class="w-3 h-3 rounded inline-block"
            style="box-shadow: 0 0 0 2px #3a3a3a; background: #f7f4f1;"
          />
          오늘
        </span>
        <span class="flex items-center gap-1.5">
          <span
            class="w-3 h-3 rounded inline-block"
            style="background: rgba(166,124,82,0.10); border: 1px solid rgba(166,124,82,0.25);"
          />
          절기
        </span>
        <span class="flex items-center gap-1.5">
          <span style="color: #2878c8;">(윤)</span>
          윤달
        </span>
      </div>
    </template>
  </div>
</template>
