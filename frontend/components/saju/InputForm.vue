<script setup lang="ts">
import type { SajuCalcRequest } from '~/types/saju'

const emit = defineEmits<{ submit: [req: SajuCalcRequest] }>()

const form = reactive({
  birth_date: '',
  birth_time: '12:00',
  gender: 'male' as 'male' | 'female',
  calendar: 'solar' as 'solar' | 'lunar',
  is_leap_month: false,
})

const HOUR_OPTIONS = [
  { label: '자시 (23:30 ~ 01:30)', value: '00:30' },
  { label: '축시 (01:30 ~ 03:30)', value: '02:30' },
  { label: '인시 (03:30 ~ 05:30)', value: '04:30' },
  { label: '묘시 (05:30 ~ 07:30)', value: '06:30' },
  { label: '진시 (07:30 ~ 09:30)', value: '08:30' },
  { label: '사시 (09:30 ~ 11:30)', value: '10:30' },
  { label: '오시 (11:30 ~ 13:30)', value: '12:30' },
  { label: '미시 (13:30 ~ 15:30)', value: '14:30' },
  { label: '신시 (15:30 ~ 17:30)', value: '16:30' },
  { label: '유시 (17:30 ~ 19:30)', value: '18:30' },
  { label: '술시 (19:30 ~ 21:30)', value: '20:30' },
  { label: '해시 (21:30 ~ 23:30)', value: '22:30' },
  { label: '시간 직접 입력', value: 'custom' },
]

const hourMode = ref<string>('오시 (11:30 ~ 13:30)')
const customTime = ref('')

function onHourSelect(e: Event) {
  const val = (e.target as HTMLSelectElement).value
  if (val !== 'custom') {
    form.birth_time = val
  }
}

function onCustomTime(e: Event) {
  form.birth_time = (e.target as HTMLInputElement).value
}

const isCustom = computed(() => form.birth_time === 'custom')

function onSubmit() {
  if (!form.birth_date) return
  emit('submit', { ...form })
}
</script>

<template>
  <form class="card space-y-5 max-w-lg w-full" @submit.prevent="onSubmit">
    <h2 class="text-lg font-bold text-indigo-300 tracking-wide">사주 정보 입력</h2>

    <!-- 생년월일 -->
    <div class="space-y-1">
      <label class="text-sm text-gray-400">생년월일</label>
      <input
        v-model="form.birth_date"
        type="date"
        min="1900-01-01"
        max="2100-12-31"
        required
        class="w-full bg-[#0f0f1a] border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
      />
    </div>

    <!-- 음양력 -->
    <div class="space-y-1">
      <label class="text-sm text-gray-400">달력 종류</label>
      <div class="flex gap-3">
        <button
          type="button"
          :class="form.calendar === 'solar' ? 'bg-indigo-600 text-white' : 'bg-[#0f0f1a] text-gray-400 border border-gray-600'"
          class="flex-1 py-2 rounded-lg text-sm font-medium transition-colors"
          @click="form.calendar = 'solar'; form.is_leap_month = false"
        >양력</button>
        <button
          type="button"
          :class="form.calendar === 'lunar' ? 'bg-indigo-600 text-white' : 'bg-[#0f0f1a] text-gray-400 border border-gray-600'"
          class="flex-1 py-2 rounded-lg text-sm font-medium transition-colors"
          @click="form.calendar = 'lunar'"
        >음력</button>
      </div>
      <label v-if="form.calendar === 'lunar'" class="flex items-center gap-2 text-sm text-gray-400 mt-1 cursor-pointer">
        <input v-model="form.is_leap_month" type="checkbox" class="accent-indigo-500" />
        윤달
      </label>
    </div>

    <!-- 출생 시각 -->
    <div class="space-y-1">
      <label class="text-sm text-gray-400">출생 시각</label>
      <select
        class="w-full bg-[#0f0f1a] border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
        @change="onHourSelect"
      >
        <option v-for="opt in HOUR_OPTIONS" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
      <input
        v-if="isCustom"
        type="time"
        :value="customTime"
        class="w-full bg-[#0f0f1a] border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500 mt-1"
        @input="onCustomTime"
      />
    </div>

    <!-- 성별 -->
    <div class="space-y-1">
      <label class="text-sm text-gray-400">성별</label>
      <div class="flex gap-3">
        <button
          type="button"
          :class="form.gender === 'male' ? 'bg-blue-700 text-white' : 'bg-[#0f0f1a] text-gray-400 border border-gray-600'"
          class="flex-1 py-2 rounded-lg text-sm font-medium transition-colors"
          @click="form.gender = 'male'"
        >남성</button>
        <button
          type="button"
          :class="form.gender === 'female' ? 'bg-pink-700 text-white' : 'bg-[#0f0f1a] text-gray-400 border border-gray-600'"
          class="flex-1 py-2 rounded-lg text-sm font-medium transition-colors"
          @click="form.gender = 'female'"
        >여성</button>
      </div>
    </div>

    <button type="submit" class="btn-primary w-full mt-2">
      사주 계산하기
    </button>
  </form>
</template>
