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
  <form
    class="relative overflow-hidden w-full space-y-6 rounded-2xl px-6 py-7"
    style="background: #ffffff; border: 1px solid #e8e2db;"
    @submit.prevent="onSubmit"
  >
    <!-- Decorative background 四柱 text -->
    <div
      class="pointer-events-none absolute -right-3 -top-4 font-serif text-[7rem] leading-none font-bold select-none"
      style="color: rgba(166,124,82,0.05); letter-spacing: 0.05em;"
      aria-hidden="true"
    >
      四柱
    </div>

    <div class="relative space-y-6">
      <!-- 생년월일 -->
      <div class="space-y-1.5">
        <label class="text-xs tracking-wider uppercase" style="color: #aaaaaa;">생년월일</label>
        <input
          v-model="form.birth_date"
          type="date"
          min="1900-01-01"
          max="2100-12-31"
          required
          class="input-underline"
        />
      </div>

      <!-- 음양력 -->
      <div class="space-y-2">
        <label class="text-xs tracking-wider uppercase" style="color: #aaaaaa;">달력 종류</label>
        <div class="flex gap-2 p-1 rounded-full" style="background: #f0ece8;">
          <button
            type="button"
            class="pill-toggle"
            :class="form.calendar === 'solar' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
            @click="form.calendar = 'solar'; form.is_leap_month = false"
          >
            양력
          </button>
          <button
            type="button"
            class="pill-toggle"
            :class="form.calendar === 'lunar' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
            @click="form.calendar = 'lunar'"
          >
            음력
          </button>
        </div>
        <label
          v-if="form.calendar === 'lunar'"
          class="flex items-center gap-2 text-xs mt-1 cursor-pointer select-none"
          style="color: #888888;"
        >
          <input
            v-model="form.is_leap_month"
            type="checkbox"
            class="w-3.5 h-3.5 rounded"
            style="accent-color: #3a3a3a;"
          />
          <span>윤달</span>
        </label>
      </div>

      <!-- 출생 시각 -->
      <div class="space-y-1.5">
        <label class="text-xs tracking-wider uppercase" style="color: #aaaaaa;">출생 시각</label>
        <select
          class="select-underline"
          @change="onHourSelect"
        >
          <option
            v-for="opt in HOUR_OPTIONS"
            :key="opt.value"
            :value="opt.value"
            style="background: #ffffff; color: #1a1a1a;"
          >
            {{ opt.label }}
          </option>
        </select>
        <input
          v-if="isCustom"
          type="time"
          :value="customTime"
          class="input-underline mt-1"
          @input="onCustomTime"
        />
      </div>

      <!-- 성별 -->
      <div class="space-y-2">
        <label class="text-xs tracking-wider uppercase" style="color: #aaaaaa;">성별</label>
        <div class="flex gap-2 p-1 rounded-full" style="background: #f0ece8;">
          <button
            type="button"
            class="pill-toggle"
            :class="form.gender === 'male' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
            @click="form.gender = 'male'"
          >
            남성
          </button>
          <button
            type="button"
            class="pill-toggle"
            :class="form.gender === 'female' ? 'pill-toggle-active' : 'pill-toggle-inactive'"
            @click="form.gender = 'female'"
          >
            여성
          </button>
        </div>
      </div>

      <button type="submit" class="btn-primary mt-2 text-base">
        사주 계산하기
      </button>
    </div>
  </form>
</template>
