<script setup lang="ts">
import type { SajuCalcRequest } from '~/types/saju'
import { useSajuStore } from '~/stores/saju'
import { useAuthStore } from '~/stores/auth'

const store = useSajuStore()
const auth = useAuthStore()
const config = useRuntimeConfig()
const base = config.public.apiBase

// ── 저장하기 ──────────────────────────────────────────────────────────────────
const saveState = ref<'idle' | 'loading' | 'done' | 'error'>('idle')

async function saveProfile() {
  if (!store.lastRequest) return
  if (!auth.isLoggedIn) {
    localStorage.setItem('pending_profile', JSON.stringify(store.lastRequest))
    navigateTo('/login')
    return
  }
  saveState.value = 'loading'
  try {
    const req = store.lastRequest
    await $fetch(`${base}/api/profiles`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${auth.token}` },
      body: {
        name: req.name?.trim() || '내 사주',
        birth_date: req.birth_date,
        birth_time: req.birth_time ?? null,
        calendar: req.calendar ?? 'solar',
        gender: req.gender,
        is_leap_month: req.is_leap_month ?? false,
        city: req.city ?? null,
        longitude: req.birth_longitude ?? null,
      },
    })
    saveState.value = 'done'
    setTimeout(() => { saveState.value = 'idle' }, 2500)
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } })?.response?.status
    saveState.value = status === 409 ? 'done' : 'error'
    setTimeout(() => { saveState.value = 'idle' }, 2500)
  }
}

// ── 공유하기 ──────────────────────────────────────────────────────────────────
const shareState = ref<'idle' | 'loading' | 'copied' | 'error'>('idle')
const shareUrl = ref('')

async function createShare() {
  if (!store.result || !store.lastRequest) return
  if (shareUrl.value) {
    await navigator.clipboard.writeText(shareUrl.value)
    shareState.value = 'copied'
    setTimeout(() => { shareState.value = 'idle' }, 2500)
    return
  }
  shareState.value = 'loading'
  try {
    const data = await $fetch<{ share_token: string; share_url: string }>(`${base}/api/share`, {
      method: 'POST',
      headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : {},
      body: {
        calc_snapshot: store.result,
        birth_input: store.lastRequest,
      },
    })
    shareUrl.value = data.share_url
    await navigator.clipboard.writeText(data.share_url)
    shareState.value = 'copied'
    setTimeout(() => { shareState.value = 'idle' }, 2500)
  } catch {
    shareState.value = 'error'
    setTimeout(() => { shareState.value = 'idle' }, 2500)
  }
}

async function onSubmit(req: SajuCalcRequest) {
  shareUrl.value = ''
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
      <SajuResultPanel :result="store.result" :input-summary="inputSummary">
        <!-- 다시 계산 버튼 -->
        <template #summary-action>
          <button class="input-summary-reset" @click="store.reset(); shareUrl = ''">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none">
              <path d="M4 4v5h5M20 20v-5h-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 9a9 9 0 0114.13-3.36L20 9M4 15l1.87 3.36A9 9 0 0020 15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            다시 계산
          </button>
        </template>

        <!-- 저장 / 공유 버튼 -->
        <template #actions>
          <div class="flex gap-3 pt-4">
            <button class="action-btn-lg" :disabled="saveState === 'loading'" @click="saveProfile">
              <svg v-if="saveState === 'loading'" class="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="32" stroke-dashoffset="12"/>
              </svg>
              <svg v-else-if="saveState === 'done'" class="w-5 h-5" viewBox="0 0 24 24" fill="none">
                <path d="M5 13l4 4L19 7" stroke="var(--color-good)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else class="w-5 h-5" viewBox="0 0 24 24" fill="none">
                <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M17 21v-8H7v8M7 3v5h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>{{ saveState === 'done' ? '저장됨' : saveState === 'error' ? '저장 오류' : '프로필 저장하기' }}</span>
            </button>

            <button class="action-btn-lg" :disabled="shareState === 'loading'" @click="createShare">
              <svg v-if="shareState === 'loading'" class="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="32" stroke-dashoffset="12"/>
              </svg>
              <svg v-else-if="shareState === 'copied'" class="w-5 h-5" viewBox="0 0 24 24" fill="none">
                <path d="M5 13l4 4L19 7" stroke="var(--color-good)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else class="w-5 h-5" viewBox="0 0 24 24" fill="none">
                <circle cx="18" cy="5" r="3" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="6" cy="12" r="3" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="18" cy="19" r="3" stroke="currentColor" stroke-width="1.5"/>
                <path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span>{{ shareState === 'copied' ? '링크 복사됨' : shareState === 'error' ? '공유 오류' : '공유하기' }}</span>
            </button>
          </div>
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

.action-btn-lg {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: var(--fs-body);
  font-weight: 600;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.action-btn-lg:hover:not(:disabled) {
  background: var(--surface-2);
}
.action-btn-lg:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
