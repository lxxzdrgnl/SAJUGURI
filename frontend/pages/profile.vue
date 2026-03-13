<script setup lang="ts">
import type { SajuCalcRequest } from '~/types/saju'
import { useSajuStore } from '~/stores/saju'
import { useAuthStore } from '~/stores/auth'

const store = useSajuStore()
const auth = useAuthStore()
const config = useRuntimeConfig()
const base = config.public.apiBase

// ── 내 만세력에서 진입한 경우 이미 저장된 상태로 표시 ──────────────────────────
const route = useRoute()

// ── 로그인 유도 모달 ──────────────────────────────────────────────────────────
const showLoginModal = ref(false)

function confirmLogin() {
  localStorage.setItem('saju_pending_save', JSON.stringify(buildProfileBody()))
  if (store.result) {
    localStorage.setItem('saju_pending_state', JSON.stringify({
      req: store.lastRequest,
      res: store.result,
    }))
  }
  navigateTo('/login')
}

// ── 저장하기 ──────────────────────────────────────────────────────────────────
const saveState = ref<'idle' | 'loading' | 'done' | 'exists' | 'error'>('idle')

function buildProfileBody() {
  const req = store.lastRequest!
  const dp = store.result?.day_pillar
  return {
    name: req.name?.trim() || '내 사주',
    birth_date: req.birth_date,
    birth_time: req.birth_time ?? null,
    calendar: req.calendar ?? 'solar',
    gender: req.gender,
    is_leap_month: req.is_leap_month ?? false,
    city: req.city ?? null,
    longitude: req.birth_longitude ?? null,
    day_stem: dp?.stem ?? null,
    day_branch: dp?.branch ?? null,
    day_stem_element: dp?.stem_element ?? null,
  }
}

async function saveProfile() {
  if (!store.lastRequest) return
  if (!auth.isLoggedIn) {
    showLoginModal.value = true
    return
  }
  saveState.value = 'loading'
  try {
    await $fetch(`${base}/api/profiles`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${auth.token}` },
      body: buildProfileBody(),
    })
    saveState.value = 'done'
    setTimeout(() => { saveState.value = 'idle' }, 2500)
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } })?.response?.status
    saveState.value = status === 409 ? 'exists' : 'error'
    setTimeout(() => { saveState.value = 'idle' }, 2500)
  }
}

// 로그인 후 복귀 시 이전 계산 결과 복원 / 내 만세력 진입 시 저장 상태 표시
onMounted(() => {
  if (route.query.saved === '1') {
    saveState.value = 'exists'
  }

  const pending = localStorage.getItem('saju_pending_state')
  if (pending) {
    try {
      const { req, res } = JSON.parse(pending)
      store.restore(req, res)
    } catch { /* ignore */ }
    localStorage.removeItem('saju_pending_state')
  }
})

// ── 공유하기 ──────────────────────────────────────────────────────────────────
const shareState = ref<'idle' | 'loading' | 'error'>('idle')
const shareUrl = ref('')
const showShareModal = ref(false)
const shareCopied = ref(false)

async function copyShareUrl() {
  await navigator.clipboard.writeText(shareUrl.value)
  shareCopied.value = true
  setTimeout(() => { shareCopied.value = false }, 2000)
}

async function createShare() {
  if (!store.result || !store.lastRequest) return
  if (shareUrl.value) {
    showShareModal.value = true
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
    shareState.value = 'idle'
    showShareModal.value = true
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
              <span>{{ saveState === 'done' ? '저장됨' : saveState === 'exists' ? '저장된 만세력' : saveState === 'error' ? '저장 오류' : '만세력 저장하기' }}</span>
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
              <span>{{ shareState === 'loading' ? '생성 중...' : shareState === 'error' ? '공유 오류' : '공유하기' }}</span>
            </button>
          </div>
        </template>
      </SajuResultPanel>
    </div>
    </Transition>

  </div>

  <!-- 공유 모달 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="showShareModal" class="modal-backdrop" @click.self="showShareModal = false">
        <div class="modal-sheet">
          <div class="modal-header">
            <p class="modal-title">공유하기</p>
            <button class="modal-close" @click="showShareModal = false">
              <svg viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </button>
          </div>
          <p class="modal-subdesc">아래 링크를 공유하세요</p>
          <div class="modal-link-box">
            <span class="modal-link-text">{{ shareUrl }}</span>
          </div>
          <button class="modal-copy-btn" @click="copyShareUrl">
            <svg v-if="shareCopied" class="w-4 h-4" viewBox="0 0 24 24" fill="none">
              <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none">
              <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            {{ shareCopied ? '복사됨!' : '링크 복사' }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- 로그인 유도 모달 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="showLoginModal" class="modal-backdrop" @click.self="showLoginModal = false">
        <div class="modal-sheet">
          <div class="modal-icon">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <p class="modal-title">로그인이 필요해요</p>
          <p class="modal-desc">만세력을 저장하려면 로그인이 필요해요.<br>로그인 후 자동으로 저장됩니다.</p>
          <div class="modal-actions">
            <button class="modal-btn modal-btn-primary" @click="confirmLogin">로그인하러 가기</button>
            <button class="modal-btn modal-btn-cancel" @click="showLoginModal = false">취소</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
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
  padding: 14px 20px;
  border-radius: 12px;
  font-size: var(--fs-body);
  font-weight: 600;
  white-space: nowrap;
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

/* ── 공유/로그인 공통 모달 ── */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: var(--surface-2);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-muted);
  flex-shrink: 0;
}
.modal-close svg { width: 16px; height: 16px; }
.modal-close:hover { background: var(--surface-3); }
.modal-subdesc {
  font-size: var(--fs-sub);
  color: var(--text-muted);
  margin-top: -4px;
}
.modal-link-box {
  background: var(--surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 12px 14px;
}
.modal-link-text {
  font-size: 13px;
  color: var(--text-secondary);
  word-break: break-all;
  display: block;
}
.modal-copy-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 13px;
  border-radius: 12px;
  border: none;
  background: var(--accent);
  color: #fff;
  font-size: var(--fs-body);
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s;
  margin-top: 4px;
}
.modal-copy-btn:hover { background: var(--accent-hover); }

/* ── 로그인 유도 모달 ── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  padding: 0 0 env(safe-area-inset-bottom, 0);
}
@media (min-width: 480px) {
  .modal-backdrop {
    align-items: center;
  }
}
.modal-sheet {
  width: 100%;
  max-width: 420px;
  background: var(--surface-1);
  border-radius: 24px 24px 0 0;
  padding: 32px 28px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  text-align: center;
}
@media (min-width: 480px) {
  .modal-sheet {
    border-radius: 24px;
    padding: 36px 32px;
  }
}
.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  margin-bottom: 4px;
}
.modal-icon svg {
  width: 24px;
  height: 24px;
}
.modal-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-primary);
}
.modal-desc {
  font-size: var(--fs-sub);
  color: var(--text-muted);
  line-height: 1.7;
  margin-bottom: 6px;
}
.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  margin-top: 4px;
}
.modal-btn {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  font-size: var(--fs-body);
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  border: none;
  transition: background 0.15s;
}
.modal-btn-primary {
  background: var(--accent);
  color: #fff;
}
.modal-btn-primary:hover { background: var(--accent-hover); }
.modal-btn-cancel {
  background: var(--surface-2);
  color: var(--text-secondary);
}
.modal-btn-cancel:hover { background: var(--surface-3); }

/* 모달 트랜지션 */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .modal-sheet,
.modal-leave-active .modal-sheet {
  transition: transform 0.25s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-sheet {
  transform: translateY(40px);
}
.modal-leave-to .modal-sheet {
  transform: translateY(40px);
}
</style>
