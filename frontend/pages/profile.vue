<script setup lang="ts">
import type { SajuCalcRequest } from '~/types/saju'
import { useSajuStore } from '~/stores/saju'
import { useAuthStore } from '~/stores/auth'
import { STORAGE_KEYS } from '~/utils/storageKeys'

const store  = useSajuStore()
const auth   = useAuthStore()
const route  = useRoute()
const config = useRuntimeConfig()

// ── 저장 모달 (프로필 0개 첫 계산 후) ────────────────────────────────────────
const showFirstSaveModal = ref(false)
const firstSaveState = ref<'idle' | 'loading' | 'done' | 'error'>('idle')

async function checkAndPromptSave() {
  if (!auth.isLoggedIn) return
  try {
    const profiles = await auth.authFetch<unknown[]>(`${config.public.apiBase}/api/profiles`)
    if (profiles.length === 0) showFirstSaveModal.value = true
  } catch { /* 무시 */ }
}

async function doFirstSave() {
  const b = store.lastRequest as Record<string, unknown>
  const dp = store.result?.day_pillar
  if (!b) return
  firstSaveState.value = 'loading'
  try {
    await auth.authFetch(`${config.public.apiBase}/api/profiles`, {
      method: 'POST',
      body: {
        name: (b.name as string)?.trim() || '내 사주',
        birth_date: b.birth_date,
        birth_time: b.birth_time ?? null,
        calendar: b.calendar ?? 'solar',
        gender: b.gender,
        is_leap_month: b.is_leap_month ?? false,
        city: b.city ?? null,
        longitude: (b.birth_longitude ?? b.longitude) ?? null,
        day_stem: dp?.stem ?? null,
        day_branch: dp?.branch ?? null,
        day_stem_element: dp?.stem_element ?? null,
      },
    })
    firstSaveState.value = 'done'
    setTimeout(() => { showFirstSaveModal.value = false; firstSaveState.value = 'idle' }, 1200)
  } catch {
    firstSaveState.value = 'error'
    setTimeout(() => { firstSaveState.value = 'idle' }, 2000)
  }
}

// 로그인 이동 시 결과 자동 저장 → 복귀 시 자동 복원
useLoginStatePersist(
  STORAGE_KEYS.SAJU_PENDING_STATE,
  () => store.result && store.lastRequest ? { req: store.lastRequest, res: store.result } : null,
  ({ req, res }) => store.restore(req, res),
)

// 페이지 떠날 때 스토어 초기화 (홈에서 프리로드한 결과가 남지 않도록)
onBeforeRouteLeave(() => { store.reset() })

async function onSubmit(req: SajuCalcRequest) {
  await store.calculate(req)
  if (store.result) checkAndPromptSave()
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
      class="transition-all duration-500"
      :class="store.result ? 'mb-4 text-center' : 'mb-6'"
    >
      <!-- 입력 화면: 뒤로가기(좌상단) + 타이틀 중앙 -->
      <div v-if="!store.result" class="relative mb-1">
        <button
          class="absolute left-0 top-1 flex items-center justify-center sm:hidden"
          style="width:32px;height:32px;border-radius:8px;border:1px solid var(--border-subtle);background:var(--surface-1);color:var(--text-secondary);cursor:pointer;"
          @click="navigateTo('/')"
        >
          <svg viewBox="0 0 24 24" fill="none" style="width:20px;height:20px;">
            <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <h1 class="font-bold tracking-wide leading-none text-5xl text-center" style="font-family: var(--font-ganji);">
          <span style="color: var(--text-primary);">사주</span><span style="color: var(--accent);">구리</span>
        </h1>
      </div>

      <!-- 결과 화면: 뒤로가기 + 타이틀 -->
      <div v-else class="relative w-full">
        <button
          class="absolute left-0 top-1/2 flex items-center justify-center sm:hidden"
          style="width:32px;height:32px;border-radius:8px;border:1px solid var(--border-subtle);background:var(--surface-1);color:var(--text-secondary);cursor:pointer;transform:translateY(-50%);"
          @click="store.reset()"
        >
          <svg viewBox="0 0 24 24" fill="none" style="width:20px;height:20px;">
            <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <h1
          class="font-bold tracking-wide leading-none text-3xl"
          style="font-family: var(--font-ganji);"
        >
          <span style="color: var(--text-primary);">사주</span><span style="color: var(--accent);">구리</span>
        </h1>
      </div>
      <p v-if="!store.result" class="mt-4 text-sm text-center" style="color: var(--text-muted);">
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
      <LoadingSpinner size="lg" />
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

  <!-- 첫 계산 후 저장 유도 모달 -->
  <AppDialog
    v-model:show="showFirstSaveModal"
    title="프로필을 저장할까요?"
    desc="저장하면 다음에 다시 입력 없이 바로 만세력을 볼 수 있어요."
    cancel-text="다음에"
  >
    <button
      class="btn-primary"
      style="width:100%"
      :disabled="firstSaveState === 'loading' || firstSaveState === 'done'"
      @click="doFirstSave"
    >
      <template v-if="firstSaveState === 'loading'">저장 중…</template>
      <template v-else-if="firstSaveState === 'done'">저장 완료!</template>
      <template v-else-if="firstSaveState === 'error'">저장 실패 — 다시 시도</template>
      <template v-else>저장하기</template>
    </button>
  </AppDialog>
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
