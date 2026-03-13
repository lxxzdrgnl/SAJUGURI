<script setup lang="ts">
import type { SajuCalcRequest } from '~/types/saju'
import {
  searchCities, calcSolarCorrection, formatCorrection, SEOUL_CORRECTION, type CityOption,
} from '~/utils/citySearch'

const emit = defineEmits<{ submit: [req: SajuCalcRequest] }>()

const form = reactive<{
  name: string
  birth_date: string
  birth_time: string | null
  gender: 'male' | 'female'
  calendar: 'solar' | 'lunar'
  is_leap_month: boolean
}>({
  name: '',
  birth_date: '',
  birth_time: '12:00',
  gender: 'male',
  calendar: 'solar',
  is_leap_month: false,
})

// ── 날짜 분리 입력 ──────────────────────────────────────────────────
const yearRef  = ref<HTMLInputElement | null>(null)
const monthRef = ref<HTMLInputElement | null>(null)
const dayRef   = ref<HTMLInputElement | null>(null)
const yearVal  = ref('')
const monthVal = ref('')
const dayVal   = ref('')

// 날짜 유효성 에러 메시지
const dateError = computed((): string | null => {
  const y = parseInt(yearVal.value)
  const m = parseInt(monthVal.value)
  const d = parseInt(dayVal.value)
  if (!yearVal.value || !monthVal.value || !dayVal.value) return null
  if (yearVal.value.length < 4) return null
  if (y < 1900 || y > 2100) return `연도는 1900년 ~ 2100년 사이여야 합니다.`
  // 월별 최대 일수 검사
  const maxDay = new Date(y, m, 0).getDate() // m월의 마지막 날 (month는 1-based)
  if (d > maxDay) return `${y}년 ${m}월은 ${maxDay}일까지 있습니다.`
  return null
})

watch([yearVal, monthVal, dayVal], () => {
  const y = yearVal.value
  const m = monthVal.value.padStart(2, '0')
  const d = dayVal.value.padStart(2, '0')
  form.birth_date = (y.length === 4 && monthVal.value && dayVal.value)
    ? `${y}-${m}-${d}` : ''
})

// ── 분리 입력 공통 팩토리 (Factory Pattern) ─────────────────────────
interface SegInputCfg {
  maxLen:          number
  maxVal?:         number
  minVal?:         number
  target:          Ref<string>
  nextFocus?:      Ref<HTMLInputElement | null>
  /** 한 자리에서 pad+자동전진 (ex. 월: 1, 시: 2) */
  eagerThreshold?: number
  /** 한 자리에서 pad만 — 전진 없음 (ex. 일: 3) */
  padThreshold?:   number
}

function makeSegInput(cfg: SegInputCfg) {
  return (e: Event) => {
    const el = e.target as HTMLInputElement
    let val = el.value.replace(/\D/g, '').slice(0, cfg.maxLen)
    if (val.length === cfg.maxLen) {
      const n = parseInt(val)
      if (cfg.maxVal !== undefined && n > cfg.maxVal) val = String(cfg.maxVal)
      if (cfg.minVal !== undefined && n < cfg.minVal) val = String(cfg.minVal).padStart(cfg.maxLen, '0')
    }
    cfg.target.value = val; el.value = val
    if (cfg.padThreshold !== undefined && val.length === 1 && parseInt(val) > cfg.padThreshold) {
      cfg.target.value = `0${val}`; el.value = cfg.target.value
      return
    }
    if (cfg.nextFocus) {
      const advance = val.length === cfg.maxLen ||
        (cfg.eagerThreshold !== undefined && val.length === 1 && parseInt(val) > cfg.eagerThreshold)
      if (advance) {
        if (val.length === 1) { cfg.target.value = `0${val}`; el.value = cfg.target.value }
        cfg.nextFocus.value?.focus()
      }
    }
  }
}

function makeBackspace(cur: Ref<string>, prevRef: Ref<HTMLInputElement | null>, prevVal: Ref<string>) {
  return (e: KeyboardEvent) => {
    if (e.key === 'Backspace' && cur.value === '') {
      e.preventDefault()
      prevRef.value?.focus()
      prevVal.value = prevVal.value.slice(0, -1)
      if (prevRef.value) prevRef.value.value = prevVal.value
    }
  }
}

// ── 날짜 분리 입력 ──────────────────────────────────────────────────
const onYearInput    = makeSegInput({ maxLen: 4,                        target: yearVal,  nextFocus: monthRef })
const onMonthInput   = makeSegInput({ maxLen: 2, maxVal: 12, minVal: 1, target: monthVal, nextFocus: dayRef,    eagerThreshold: 1 })
const onDayInput     = makeSegInput({ maxLen: 2, maxVal: 31, minVal: 1, target: dayVal,   padThreshold: 3 })
const onMonthKeydown = makeBackspace(monthVal, yearRef,  yearVal)
const onDayKeydown   = makeBackspace(dayVal,   monthRef, monthVal)

// ── 시각 분리 입력 ──────────────────────────────────────────────────
const hourRef     = ref<HTMLInputElement | null>(null)
const minuteRef   = ref<HTMLInputElement | null>(null)
const hourVal     = ref('12')
const minuteVal   = ref('00')
const timeUnknown = ref(false)

watch([hourVal, minuteVal], () => {
  if (timeUnknown.value) return
  const h = hourVal.value.padStart(2, '0')
  const m = minuteVal.value.padStart(2, '0')
  if (hourVal.value !== '' && minuteVal.value !== '') form.birth_time = `${h}:${m}`
})

watch(timeUnknown, (v) => {
  form.birth_time = v ? null : `${hourVal.value.padStart(2,'0')}:${minuteVal.value.padStart(2,'0')}`
})

const onHourInput     = makeSegInput({ maxLen: 2, maxVal: 23, target: hourVal,   nextFocus: minuteRef, eagerThreshold: 2 })
const onMinuteInput   = makeSegInput({ maxLen: 2, maxVal: 59, target: minuteVal })
const onMinuteKeydown = makeBackspace(minuteVal, hourRef, hourVal)

// ── 도시 검색 ────────────────────────────────────────────────────────
const cityQuery    = ref('')
const cityResults  = ref<CityOption[]>([])
const selectedCity = ref<CityOption | null>(null)
const cityOpen     = ref(false)
const cityInputRef = ref<HTMLInputElement | null>(null)
const cityLoading  = ref(false)

const correction = computed(() => {
  const city = selectedCity.value
  if (!city) return SEOUL_CORRECTION
  return calcSolarCorrection(city.longitude, city.utcOffset)
})

let _debounceTimer: ReturnType<typeof setTimeout> | null = null

// 시시(時辰) 목록 — 시작 분(0~1439) 기준
const SISI: { name: string; hanja: string; start: number; end: number; range: string }[] = [
  { name: '자시', hanja: '子時', start: 23*60+30, end: 25*60+30, range: '23:30~01:30' },
  { name: '축시', hanja: '丑時', start:  1*60+30, end:  3*60+30, range: '01:30~03:30' },
  { name: '인시', hanja: '寅時', start:  3*60+30, end:  5*60+30, range: '03:30~05:30' },
  { name: '묘시', hanja: '卯時', start:  5*60+30, end:  7*60+30, range: '05:30~07:30' },
  { name: '진시', hanja: '辰時', start:  7*60+30, end:  9*60+30, range: '07:30~09:30' },
  { name: '사시', hanja: '巳時', start:  9*60+30, end: 11*60+30, range: '09:30~11:30' },
  { name: '오시', hanja: '午時', start: 11*60+30, end: 13*60+30, range: '11:30~13:30' },
  { name: '미시', hanja: '未時', start: 13*60+30, end: 15*60+30, range: '13:30~15:30' },
  { name: '신시', hanja: '申時', start: 15*60+30, end: 17*60+30, range: '15:30~17:30' },
  { name: '유시', hanja: '酉時', start: 17*60+30, end: 19*60+30, range: '17:30~19:30' },
  { name: '술시', hanja: '戌時', start: 19*60+30, end: 21*60+30, range: '19:30~21:30' },
  { name: '해시', hanja: '亥時', start: 21*60+30, end: 23*60+30, range: '21:30~23:30' },
]

function getSisi(totalMin: number) {
  const t = ((totalMin % 1440) + 1440) % 1440
  if (t >= 23*60+30 || t < 1*60+30) return SISI[0]
  return SISI.find(s => t >= s.start && t < s.end) ?? null
}

function fmtMinutes(min: number) {
  const t = ((min % 1440) + 1440) % 1440
  const h = String(Math.floor(t / 60)).padStart(2, '0')
  const m = String(t % 60).padStart(2, '0')
  return `${h}:${m}`
}

// 보정 적용 후 시각 + 시시 미리보기
const correctedPreview = computed(() => {
  const h = parseInt(hourVal.value || '0')
  const m = parseInt(minuteVal.value || '0')
  if (isNaN(h) || isNaN(m)) return null
  const inputMin  = h * 60 + m
  const corrMin   = correction.value
  const appliedMin = inputMin + corrMin
  const sisi = getSisi(appliedMin)
  return {
    correction: corrMin,
    applied: fmtMinutes(appliedMin),
    sisi,
  }
})

function onCityInput(e: Event) {
  const q = (e.target as HTMLInputElement).value
  cityQuery.value = q
  selectedCity.value = null
  if (!q.trim()) { cityResults.value = []; cityOpen.value = false; return }
  if (_debounceTimer) clearTimeout(_debounceTimer)
  cityLoading.value = true
  _debounceTimer = setTimeout(async () => {
    cityResults.value = await searchCities(q)
    cityLoading.value = false
    cityOpen.value = cityResults.value.length > 0
  }, 300)
}

function selectCity(city: CityOption) {
  selectedCity.value = city
  cityQuery.value = city.label
  cityResults.value = []
  cityOpen.value = false
}

function clearCity() {
  selectedCity.value = null
  cityQuery.value = ''
  cityResults.value = []
  cityOpen.value = false
  nextTick(() => cityInputRef.value?.focus())
}

function onCityBlur() {
  setTimeout(() => { cityOpen.value = false }, 150)
}

// ── 제출 ─────────────────────────────────────────────────────────────
const submitAttempted = ref(false)
const nameError = computed((): string | null =>
  form.name.trim() ? null : '이름을 입력해 주세요.'
)
const birthDateError = computed((): string | null => {
  if (!submitAttempted.value) return dateError.value
  if (!form.birth_date) return '생년월일을 입력해 주세요.'
  return dateError.value
})

function onSubmit() {
  submitAttempted.value = true
  if (nameError.value || !form.birth_date || dateError.value) return
  // 도시를 타이핑만 하고 선택 안 한 경우 입력 초기화
  if (cityQuery.value && !selectedCity.value) {
    cityQuery.value = ''
    cityResults.value = []
  }
  const req: SajuCalcRequest = { ...form }
  if (selectedCity.value) {
    req.birth_longitude = selectedCity.value.longitude
    if (!selectedCity.value.isKorea) req.birth_utc_offset = selectedCity.value.utcOffset
  }
  emit('submit', req)
}
</script>

<template>
  <form
    class="relative w-full space-y-7 rounded-2xl px-8 pt-5 pb-6"
    style="background: var(--surface-1); border: 1px solid var(--border-subtle);"
    @submit.prevent="onSubmit"
  >
    <div
      class="pointer-events-none absolute -right-3 -top-4 text-[7rem] leading-none font-bold select-none"
      style="font-family: var(--font-ganji); color: rgba(166,124,82,0.04); letter-spacing: 0.05em; overflow: hidden; max-width: 60%;"
      aria-hidden="true"
    >四柱</div>

    <div class="relative space-y-4">

      <!-- 이름 -->
      <div class="space-y-1">
        <label class="text-sm font-semibold tracking-wide" style="color: var(--text-muted);">이름 <span style="color: var(--color-bad);">*</span></label>
        <input v-model="form.name" type="text" placeholder="홍길동"
          class="input-underline" style="font-size: 18px;" />
        <p v-if="submitAttempted && nameError" class="text-xs font-medium" style="color: var(--color-bad);">
          {{ nameError }}
        </p>
      </div>

      <!-- 출생지 -->
      <div class="space-y-1">
        <label class="text-sm font-semibold tracking-wide" style="color: var(--text-muted);">출생지</label>
        <div class="relative">
          <div class="flex items-center gap-2" style="border-bottom: 1px solid var(--border-default);">
            <svg class="w-4 h-4 flex-shrink-0" style="color: var(--text-muted);" fill="none"
              stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input ref="cityInputRef" type="text" :value="cityQuery"
              placeholder="도시명 검색 (예: 서울, 도쿄, 뉴욕)"
              class="city-input" style="font-size: 15px; padding: 6px 0;"
              autocomplete="off"
              @input="onCityInput"
              @focus="cityOpen = cityResults.length > 0"
              @blur="onCityBlur" />
            <button v-if="selectedCity" type="button"
              class="flex-shrink-0 text-sm" style="color: var(--text-muted);"
              @click="clearCity">✕</button>
          </div>
          <ul v-if="cityLoading" class="city-dropdown">
            <li class="city-item" style="color: var(--text-muted);">검색 중...</li>
          </ul>
          <ul v-else-if="cityOpen && cityResults.length" class="city-dropdown">
            <li v-for="city in cityResults" :key="city.label + city.timezone"
              class="city-item" @mousedown.prevent="selectCity(city)">
              <span class="city-item-label">{{ city.label }}</span>
              <span class="city-item-sub">{{ city.sublabel }}</span>
            </li>
          </ul>
        </div>
        <p class="text-xs" style="color: var(--text-muted);">
          {{ selectedCity ? selectedCity.timezone : '미입력 시 서울 기준 적용' }}
        </p>
      </div>

      <!-- 생년월일 + 시각 (한 줄) -->
      <div class="space-y-1">
        <div class="flex items-center justify-between">
          <span class="fs-label tracking-wider uppercase" style="color: var(--text-muted);">생년월일 · 시각</span>
          <label class="flex items-center gap-1 cursor-pointer select-none fs-label" style="color: var(--text-muted);">
            <input type="checkbox" v-model="timeUnknown" class="accent-amber-700" style="width: 12px; height: 12px;" />
            시간 모름
          </label>
        </div>
        <!-- 날짜 + 시각 + 토글 -->
        <div class="flex flex-wrap items-center gap-y-2 gap-x-3">
          <!-- 날짜 + 시각 입력 -->
          <div class="flex-1 min-w-0 flex items-baseline" style="border-bottom: 1px solid var(--border-default); min-width: 200px;">
            <input ref="yearRef" type="text" inputmode="numeric" placeholder="YYYY" maxlength="4"
              class="date-seg" style="flex: 2; min-width: 0;" @input="onYearInput" />
            <span class="date-sep" style="padding: 0 1px;">/</span>
            <input ref="monthRef" type="text" inputmode="numeric" placeholder="MM" maxlength="2"
              class="date-seg" style="flex: 1; min-width: 0;"
              @input="onMonthInput" @keydown="onMonthKeydown" />
            <span class="date-sep" style="padding: 0 1px;">/</span>
            <input ref="dayRef" type="text" inputmode="numeric" placeholder="DD" maxlength="2"
              class="date-seg" style="flex: 1; min-width: 0;"
              @input="onDayInput" @keydown="onDayKeydown" />
            <span class="date-sep" style="padding: 0 4px; color: var(--border-default);">·</span>
            <span v-if="!timeUnknown" class="flex items-baseline" style="flex: 2; min-width: 0;">
              <input ref="hourRef" type="text" inputmode="numeric" placeholder="HH" maxlength="2"
                :value="hourVal" class="date-seg" style="flex: 1; min-width: 0;"
                @input="onHourInput" />
              <span class="date-sep" style="padding: 0 1px;">:</span>
              <input ref="minuteRef" type="text" inputmode="numeric" placeholder="MM" maxlength="2"
                :value="minuteVal" class="date-seg" style="flex: 1; min-width: 0;"
                @input="onMinuteInput" @keydown="onMinuteKeydown" />
            </span>
            <span v-else class="date-seg" style="flex: 2; min-width: 0; color: var(--text-muted); font-size: 14px; padding-bottom: 2px;">시간 모름</span>
          </div>
          <!-- 양력/음력/윤달 토글 -->
          <div class="flex gap-1 p-0.5 rounded-full shrink-0 w-full sm:w-auto" style="background: var(--surface-3);">
            <button type="button" class="pill-toggle !text-xs !px-3 !py-1"
              :class="form.calendar === 'solar' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
              @click="form.calendar = 'solar'; form.is_leap_month = false">양력</button>
            <button type="button" class="pill-toggle !text-xs !px-3 !py-1"
              :class="form.calendar === 'lunar' && !form.is_leap_month ? 'pill-toggle-active' : 'pill-toggle-inactive'"
              @click="form.calendar = 'lunar'; form.is_leap_month = false">음력</button>
            <button type="button" class="pill-toggle !text-xs !px-3 !py-1 transition-opacity"
              :class="form.calendar === 'lunar' && form.is_leap_month ? 'pill-toggle-active' : 'pill-toggle-inactive'"
              :style="form.calendar !== 'lunar' ? 'opacity: 0.35; cursor: default;' : ''"
              :disabled="form.calendar !== 'lunar'"
              @click="form.is_leap_month = !form.is_leap_month">윤달</button>
          </div>
        </div>
        <!-- 보정 미리보기 -->
        <div v-if="!timeUnknown && correctedPreview && (hourVal || minuteVal)"
          class="flex items-center gap-1.5 text-xs flex-wrap" style="color: var(--text-muted);">
          <span>{{ formatCorrection(correctedPreview.correction) }} 보정</span>
          <span style="color: var(--text-muted);">→</span>
          <span style="color: var(--text-secondary); font-variant-numeric: tabular-nums;">{{ correctedPreview.applied }}</span>
          <span v-if="correctedPreview.sisi"
            class="px-1.5 py-0.5 rounded font-medium"
            style="background: var(--surface-3); color: var(--text-muted);">
            {{ correctedPreview.sisi.name }}({{ correctedPreview.sisi.hanja }})
          </span>
          <span v-if="correctedPreview.sisi" style="color: var(--text-muted);">{{ correctedPreview.sisi.range }}</span>
        </div>
        <!-- 날짜 유효성 에러 -->
        <p v-if="birthDateError" class="text-xs font-medium" style="color: var(--color-bad);">
          {{ birthDateError }}
        </p>
        <!-- 시간 모름 안내 -->
        <p v-if="timeUnknown" class="text-xs" style="color: var(--text-muted);">
          시주(時柱) 미산출 — 자녀·노년운, 시신살 등 시주 관련 분석이 생략됩니다.
        </p>
      </div>

      <!-- 성별 -->
      <div class="space-y-1">
        <label class="text-sm font-semibold tracking-wide" style="color: var(--text-muted);">성별</label>
        <div class="flex gap-2 p-1 rounded-full w-full" style="background: var(--surface-3);">
          <button type="button" class="pill-toggle flex-1"
            :class="form.gender === 'male' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
            @click="form.gender = 'male'">남성</button>
          <button type="button" class="pill-toggle flex-1"
            :class="form.gender === 'female' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
            @click="form.gender = 'female'">여성</button>
        </div>
      </div>

      <button
        type="submit"
        class="btn-primary w-full mt-1 text-base"
        :disabled="submitAttempted && !!(nameError || birthDateError)"
        :style="submitAttempted && (nameError || birthDateError) ? 'opacity: 0.45; cursor: not-allowed;' : ''"
      >
        사주 계산하기
      </button>
    </div>
  </form>
</template>
