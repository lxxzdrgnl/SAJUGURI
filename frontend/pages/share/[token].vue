<script setup lang="ts">
import type { SajuCalcResponse } from '~/types/saju'
import { useAuthStore } from '~/stores/auth'

const route = useRoute()
const config = useRuntimeConfig()
const auth = useAuthStore()
const token = route.params.token as string

const pending = ref(true)
const fetchError = ref(false)
const result = ref<SajuCalcResponse | null>(null)
const birthInput = ref<Record<string, unknown> | null>(null)

onMounted(async () => {
  try {
    const data = await $fetch<{
      calc_snapshot: SajuCalcResponse
      birth_input: Record<string, unknown> | null
    }>(`${config.public.apiBase}/api/share/${token}`)
    result.value = data.calc_snapshot
    birthInput.value = data.birth_input
  } catch {
    fetchError.value = true
  } finally {
    pending.value = false
  }
})

const showShareModal = ref(false)
const copied = ref(false)
const currentUrl = ref('')

onMounted(() => {
  currentUrl.value = window.location.href
})

async function copyLink() {
  await navigator.clipboard.writeText(currentUrl.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

// ── 저장하기 ──
const saveState = ref<'idle' | 'loading' | 'done' | 'exists' | 'error'>('idle')
const showLoginModal = ref(false)

async function saveProfile() {
  if (!birthInput.value) return
  if (!auth.isLoggedIn) {
    const b = birthInput.value
    const dp = result.value?.day_pillar
    localStorage.setItem('saju_pending_save', JSON.stringify({
      name: (b.name as string)?.trim() || '내 사주',
      birth_date: b.birth_date,
      birth_time: b.birth_time ?? null,
      calendar: b.calendar ?? 'solar',
      gender: b.gender,
      is_leap_month: b.is_leap_month ?? false,
      city: b.city ?? null,
      longitude: b.longitude ?? null,
      day_stem: dp?.stem ?? null,
      day_branch: dp?.branch ?? null,
      day_stem_element: dp?.stem_element ?? null,
    }))
    showLoginModal.value = true
    return
  }
  saveState.value = 'loading'
  const b = birthInput.value
  const dp = result.value?.day_pillar
  try {
    await $fetch(`${config.public.apiBase}/api/profiles`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${auth.token}` },
      body: {
        name: (b.name as string)?.trim() || '내 사주',
        birth_date: b.birth_date,
        birth_time: b.birth_time ?? null,
        calendar: b.calendar ?? 'solar',
        gender: b.gender,
        is_leap_month: b.is_leap_month ?? false,
        city: b.city ?? null,
        longitude: b.longitude ?? null,
        day_stem: dp?.stem ?? null,
        day_branch: dp?.branch ?? null,
        day_stem_element: dp?.stem_element ?? null,
      },
    })
    saveState.value = 'done'
    setTimeout(() => { saveState.value = 'idle' }, 2500)
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } })?.response?.status
    saveState.value = status === 409 ? 'exists' : 'error'
    setTimeout(() => { saveState.value = 'idle' }, 2500)
  }
}

function confirmLogin() {
  navigateTo('/login')
}

const inputSummary = computed(() => {
  const b = birthInput.value
  if (!b) return null
  const [y, m, d] = (b.birth_date as string).split('-')
  const cal = b.calendar === 'lunar'
    ? (b.is_leap_month ? '음력 윤달' : '음력')
    : '양력'
  return {
    name: (b.name as string) || '',
    date: `${y}년 ${m}월 ${d}일 (${cal})`,
    time: (b.birth_time as string) ?? '시간 모름',
    gender: b.gender === 'male' ? '남성' : '여성',
    city: (b.city as string) ?? null,
  }
})
</script>

<template>
  <div class="flex flex-col pt-3 pb-6 px-4">

    <!-- 헤더 -->
    <header class="text-center mb-6">
      <h1
        class="font-bold tracking-wide leading-none text-3xl"
        style="font-family: var(--font-ganji);"
      >
        <span style="color: var(--text-primary);">사주</span><span style="color: var(--accent);">구리</span>
      </h1>
    </header>

    <!-- 로딩 -->
    <div v-if="pending" class="mt-16 flex flex-col items-center gap-4" style="color: var(--text-muted);">
      <div class="relative w-10 h-10">
        <svg class="animate-spin w-10 h-10 absolute inset-0" viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
          <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
        </svg>
      </div>
      <span class="text-sm tracking-wide">불러오는 중...</span>
    </div>

    <!-- 에러 -->
    <div
      v-else-if="fetchError"
      class="mt-16 max-w-md mx-auto text-center space-y-3"
    >
      <p class="text-lg font-semibold" style="color: var(--text-primary);">공유 링크를 찾을 수 없습니다.</p>
      <p class="text-sm" style="color: var(--text-muted);">링크가 만료되었거나 잘못된 주소입니다.</p>
      <NuxtLink to="/" class="inline-block mt-4 btn-primary px-6">홈으로</NuxtLink>
    </div>

    <!-- 결과 -->
    <div v-else-if="result" class="max-w-5xl w-full mx-auto">
      <SajuResultPanel :result="result" :input-summary="inputSummary">
        <!-- CTA -->
        <template #actions>
          <div class="actions-wrap">
            <!-- 저장 + 공유 버튼 행 -->
            <div class="action-row">
              <button class="action-btn" :disabled="saveState === 'loading'" @click="saveProfile">
                <svg v-if="saveState === 'loading'" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="32" stroke-dashoffset="12"/>
                </svg>
                <svg v-else-if="saveState === 'done'" class="w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <path d="M5 13l4 4L19 7" stroke="var(--color-good)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M17 21v-8H7v8M7 3v5h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                {{ saveState === 'done' ? '저장됨' : saveState === 'exists' ? '저장된 만세력' : saveState === 'error' ? '저장 오류' : '만세력 저장하기' }}
              </button>

              <button class="action-btn share-btn" @click="showShareModal = true">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none">
                <circle cx="18" cy="5" r="3" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="6" cy="12" r="3" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="18" cy="19" r="3" stroke="currentColor" stroke-width="1.5"/>
                <path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              공유하기
              </button>
            </div>

            <!-- 나도 확인해보기 CTA -->
            <div class="cta-card">
              <div class="cta-text">
                <p class="cta-title">나도 내 사주가 궁금하다면?</p>
                <p class="cta-desc">생년월일시만 입력하면 무료로 사주를 확인할 수 있어요.</p>
              </div>
              <NuxtLink to="/" class="btn-primary cta-btn">
                나도 확인해보기
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </NuxtLink>
            </div>
          </div>
        </template>
      </SajuResultPanel>
    </div>

  </div>

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

  <!-- 공유 모달 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="showShareModal" class="modal-backdrop" @click.self="showShareModal = false">
        <div class="modal-sheet">
          <div class="modal-header">
            <p class="modal-title">공유하기</p>
            <button class="modal-close" @click="showShareModal = false">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <p class="modal-desc">아래 링크를 공유하세요</p>
          <div class="modal-link-box">
            <span class="modal-link-text">{{ currentUrl }}</span>
          </div>
          <button class="modal-copy-btn" @click="copyLink">
            <svg v-if="copied" class="w-4 h-4" viewBox="0 0 24 24" fill="none">
              <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none">
              <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ copied ? '복사됨!' : '링크 복사' }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.actions-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.action-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  color: var(--text-primary);
  font-size: var(--fs-body);
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}
.action-btn:hover:not(:disabled) { background: var(--surface-2); }
.action-btn:disabled { opacity: 0.6; cursor: default; }
.share-btn { flex-shrink: 0; }

.cta-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 28px;
  border-radius: 16px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
}
.cta-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.cta-title {
  font-size: var(--fs-body);
  font-weight: 700;
  color: var(--text-primary);
}
.cta-desc {
  font-size: var(--fs-sub);
  color: var(--text-muted);
}
.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  padding: 12px 20px;
  width: auto;
  flex-shrink: 0;
}
@media (max-width: 640px) {
  .cta-card {
    flex-direction: column;
    align-items: flex-start;
  }
  .cta-btn {
    width: 100%;
    justify-content: center;
  }
}

/* ── 모달 공통 ── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}
@media (min-width: 480px) { .modal-backdrop { align-items: center; } }
.modal-sheet {
  width: 100%;
  max-width: 440px;
  background: var(--surface-1);
  border-radius: 24px 24px 0 0;
  padding: 32px 24px 40px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: center;
}
@media (min-width: 480px) { .modal-sheet { border-radius: 24px; padding: 32px 28px; } }
/* 공유 모달은 왼쪽 정렬 */
.modal-sheet:has(.modal-header) { text-align: left; }
.modal-icon {
  width: 48px; height: 48px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  display: flex; align-items: center; justify-content: center;
  color: var(--accent);
  margin: 0 auto 4px;
}
.modal-icon svg { width: 24px; height: 24px; }
.modal-title { font-size: 18px; font-weight: 800; color: var(--text-primary); }
.modal-desc { font-size: var(--fs-sub); color: var(--text-muted); line-height: 1.7; margin-bottom: 6px; }
.modal-actions { display: flex; flex-direction: column; gap: 8px; width: 100%; margin-top: 4px; }
.modal-btn {
  width: 100%; padding: 14px; border-radius: 12px;
  font-size: var(--fs-body); font-weight: 600; font-family: inherit;
  cursor: pointer; border: none; transition: background 0.15s;
}
.modal-btn-primary { background: var(--accent); color: #fff; }
.modal-btn-primary:hover { background: var(--accent-hover); }
.modal-btn-cancel { background: var(--surface-2); color: var(--text-secondary); }
.modal-btn-cancel:hover { background: var(--surface-3); }

/* ── 공유 모달 전용 ── */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-align: left;
}
.modal-close {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border: none; background: var(--surface-2);
  border-radius: 8px; cursor: pointer; color: var(--text-muted);
  flex-shrink: 0;
}
.modal-close svg { width: 16px; height: 16px; }
.modal-close:hover { background: var(--surface-3); }
.modal-subdesc { font-size: var(--fs-sub); color: var(--text-muted); text-align: left; }
.modal-link-box {
  background: var(--surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 12px 14px;
  overflow: hidden;
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

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .modal-sheet, .modal-leave-active .modal-sheet { transition: transform 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-sheet, .modal-leave-to .modal-sheet { transform: translateY(40px); }
</style>
