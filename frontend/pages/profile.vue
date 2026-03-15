<script setup lang="ts">
import type { SajuCalcRequest } from '~/types/saju'
import { useSajuStore } from '~/stores/saju'

const store = useSajuStore()
const route = useRoute()

// 로그인 후 복귀 시 이전 계산 결과 복원 / 내 만세력 진입 시 저장 상태 표시
onMounted(() => {
  const pending = localStorage.getItem('saju_pending_state')
  if (pending) {
    try {
      const { req, res } = JSON.parse(pending)
      store.restore(req, res)
    } catch { /* ignore */ }
    localStorage.removeItem('saju_pending_state')
  }
})

async function onSubmit(req: SajuCalcRequest) {
  await store.calculate(req)
}

// ── 입력 요약 ──────────────────────────────────────────────────────────────────
const inputSummary = computed(() => {
  const r = store.lastRequest
  if (!r) return null
  const [y, m, d] = r.birth_date.split('-')
  const calendarLabel = r.calendar === 'lunar'
    ? (r.is_leap_month ? '음력 윤달' : '음력')
    : '양력'
  return {
    name: r.name || '',
    date: `${y}년 ${m}월 ${d}일 (${calendarLabel})`,
    time: r.birth_time ?? '시간 모름',
    gender: r.gender === 'male' ? '남성' : '여성',
    city: r.city ?? null,
  }
})
</script>

<template>
  <div class="flex flex-col pt-3 pb-6 px-4">

    <!-- 헤더 -->
    <header
      class="text-center transition-all duration-500"
      :class="store.result ? 'mb-4' : 'mb-6'"
    >
      <div class="inline-block">
        <h1
          class="font-bold tracking-wide leading-none"
          :class="store.result ? 'text-3xl' : 'text-5xl'"
          style="transition: font-size 0.4s ease; font-family: var(--font-ganji);"
        >
          <span style="color: var(--text-primary);">사주</span><span style="color: var(--accent);">구리</span>
        </h1>
        <div
          v-if="!store.result"
          class="mt-1 text-[10px] tracking-[0.35em] uppercase"
          style="color: var(--text-muted);"
        >
          四柱八字 · AI 사주 상담
        </div>
      </div>
      <p v-if="!store.result" class="mt-4 text-sm" style="color: var(--text-muted);">
        오직 당신을 위한 사주
      </p>
    </header>

    <!-- 입력 폼 -->
    <div
      class="w-full mx-auto transition-all duration-500"
      :class="store.result ? 'max-w-3xl' : 'max-w-lg'"
    >
      <ClientOnly v-if="!store.result">
        <SajuInputForm @submit="onSubmit" />
        <template #fallback>
          <div class="rounded-2xl px-8 py-8" style="background:var(--surface-1); border:1px solid var(--border-subtle); min-height: 420px;" />
        </template>
      </ClientOnly>
    </div>

    <!-- 로딩 -->
    <div v-if="store.loading" class="mt-12 flex flex-col items-center gap-4" style="color: var(--text-muted);">
      <div class="relative w-10 h-10">
        <svg class="animate-spin w-10 h-10 absolute inset-0" viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
          <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
        </svg>
      </div>
      <span class="text-sm tracking-wide" style="color: var(--text-muted);">사주를 계산하는 중...</span>
    </div>

    <!-- 에러 -->
    <div
      v-if="store.error"
      class="mt-6 max-w-xl mx-auto w-full rounded-xl px-5 py-4 text-sm"
      style="background: rgba(212,63,63,0.05); border: 1px solid rgba(212,63,63,0.18); color: #c03030;"
    >
      {{ store.error }}
    </div>

    <!-- 결과 -->
    <Transition name="result">
    <div
      v-if="store.result && !store.loading"
      class="mt-10 max-w-5xl w-full mx-auto"
    >
      <SajuResultPanel
        :result="store.result"
        :input-summary="inputSummary"
        :birth-input="(store.lastRequest as unknown as Record<string, unknown>)"
        :initial-saved="route.query.saved === '1'"
      >
        <!-- 다시 계산 버튼 -->
        <template #summary-action>
          <button class="input-summary-reset" @click="store.reset()">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none">
              <path d="M4 4v5h5M20 20v-5h-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 9a9 9 0 0114.13-3.36L20 9M4 15l1.87 3.36A9 9 0 0020 15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            다시 계산
          </button>
        </template>
      </SajuResultPanel>
    </div>
    </Transition>

  </div>
</template>

<style scoped>
.input-summary-reset {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--surface-2);
  color: var(--text-secondary);
  font-size: var(--fs-sub);
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
  flex-shrink: 0;
  align-self: flex-start;
}
.input-summary-reset:hover {
  background: var(--surface-3);
}
@media (max-width: 640px) {
  .input-summary-reset {
    width: 100%;
    justify-content: center;
  }
}
</style>
