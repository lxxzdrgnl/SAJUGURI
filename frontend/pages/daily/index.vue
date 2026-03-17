<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import type { SajuCalcRequest, DailyFortuneResponse, ProfileResponse } from '~/types/saju'
import { calcTodayIlju, formatTodayLabel, STEM_HANJA, BRANCH_HANJA, STEM_ELEMENT as STEM_EL, BRANCH_ELEMENT as BRANCH_EL, iljuColor as elColor } from '~/utils/ganji'
import { STORAGE_KEYS } from '~/utils/storageKeys'

const auth   = useAuthStore()
const { getDailyFortune, createDailyShare: _createDailyShare, getProfiles } = useSajuApi()

// ── 상태 ────────────────────────────────────────────────────────────────────
type Step = 'select' | 'input' | 'profile' | 'result'

const step            = ref<Step>('select')
const result          = ref<DailyFortuneResponse | null>(null)
const userName        = ref('')
const profiles        = ref<ProfileResponse[]>([])
const showLoginDialog = ref(false)
const fromDirectInput = ref(false)

const { loading,               error,  run: runCalc     } = useAsync()
const { loading: profLoad,             run: runProfiles  } = useAsync()

// ── 프로필 저장 ──────────────────────────────────────────────────────────────
const { saveState: saveProfileState, saveProfile: _saveProfile, saveLabel: saveProfileLabel, saveDisabled: saveProfileDisabled } = useProfileSave()

async function saveProfile() {
  if (!auth.isLoggedIn) { showLoginDialog.value = true; return }
  if (!lastBirthInput.value) return
  const b = lastBirthInput.value
  await _saveProfile({
    name:          (b.name as string)?.trim() || '내 사주',
    birth_date:    b.birth_date as string,
    birth_time:    (b.birth_time as string | null) ?? null,
    calendar:      (b.calendar as string) ?? 'solar',
    gender:        b.gender as string,
    is_leap_month: (b.is_leap_month as boolean) ?? false,
    city:          (b.city as string | null) ?? null,
    longitude:     (b.birth_longitude as number | null) ?? null,
  })
}

// ── 공유 상태 ────────────────────────────────────────────────────────────────
const shareState    = ref<'idle' | 'loading' | 'error'>('idle')
const shareUrl      = ref('')
const showShareModal = ref(false)
const lastBirthInput = ref<Record<string, unknown> | null>(null)

async function doShare() {
  if (shareUrl.value) { showShareModal.value = true; return }
  if (!lastBirthInput.value) return
  shareState.value = 'loading'
  try {
    const data = await _createDailyShare(lastBirthInput.value)
    shareUrl.value = data.share_url
    shareState.value = 'idle'
    showShareModal.value = true
  } catch {
    shareState.value = 'error'
    setTimeout(() => { shareState.value = 'idle' }, 2500)
  }
}


// ── 오늘 날짜 ────────────────────────────────────────────────────────────────
const todayLabel = formatTodayLabel()
const todayIlju  = calcTodayIlju()

// ── 프로필 로드 ──────────────────────────────────────────────────────────────
async function loadProfiles() {
  if (!auth.isLoggedIn) return
  profiles.value = (await runProfiles(() => getProfiles(auth.token as string))) ?? []
}

function goProfile() {
  if (!auth.isLoggedIn) {
    showLoginDialog.value = true
    return
  }
  loadProfiles()
  step.value = 'profile'
}

const goToLogin = useGoToLogin()
function goLogin() { goToLogin() }

// ── 로그인 이동 시 자동 저장 → 복귀 시 자동 복원 ──────────────────────────────
useLoginStatePersist(
  STORAGE_KEYS.DAILY_PENDING_INPUT,
  () => lastBirthInput.value
    ? { birthInput: lastBirthInput.value, result: result.value, userName: userName.value }
    : null,
  ({ birthInput: b, result: savedResult, userName: savedName }) => {
    fromDirectInput.value = true
    lastBirthInput.value = b
    if (savedResult) {
      result.value = savedResult
      userName.value = savedName || b?.name || '나'
      step.value = 'result'
    } else {
      step.value = 'input'
      calcFortune({
        birth_date:      b.birth_date,
        birth_time:      b.birth_time ?? null,
        gender:          b.gender,
        calendar:        b.calendar ?? 'solar',
        is_leap_month:   b.is_leap_month ?? false,
        birth_longitude: b.birth_longitude ?? undefined,
      }, b.name || '')
    }
  },
)

// ── 계산 ────────────────────────────────────────────────────────────────────
async function calcFortune(req: SajuCalcRequest, name: string) {
  userName.value = name || '나'
  shareUrl.value = ''   // 새 계산마다 공유 URL 초기화
  lastBirthInput.value = {
    name:            req.name ?? name,
    birth_date:      req.birth_date,
    birth_time:      req.birth_time ?? null,
    gender:          req.gender,
    calendar:        req.calendar ?? 'solar',
    is_leap_month:   req.is_leap_month ?? false,
    birth_longitude: req.birth_longitude ?? null,
  }
  const r = await runCalc(
    () => getDailyFortune({
      birth_date:      req.birth_date,
      birth_time:      req.birth_time,
      gender:          req.gender,
      calendar:        req.calendar,
      is_leap_month:   req.is_leap_month,
      birth_longitude: req.birth_longitude,
    }),
    '운세를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.',
  )
  if (r) { result.value = r; step.value = 'result' }
}

function onFormSubmit(req: SajuCalcRequest) {
  fromDirectInput.value = true
  calcFortune(req, req.name ?? '')
}

function onProfileSelect(p: ProfileResponse) {
  fromDirectInput.value = false
  calcFortune({
    birth_date:    p.birth_date,
    birth_time:    p.birth_time,
    gender:        p.gender as 'male' | 'female',
    calendar:      p.calendar as 'solar' | 'lunar',
    is_leap_month: p.is_leap_month,
  }, p.name)
}

function reset() {
  result.value        = null
  error.value         = ''
  step.value          = 'select'
  fromDirectInput.value  = false
  saveProfileState.value = 'idle'
}

</script>

<template>
  <div class="daily-wrap">

    <!-- 공통 헤더 -->
    <div class="daily-header">
      <button class="back-btn" @click="step === 'select' ? navigateTo('/') : step === 'result' ? reset() : (step = 'select')">
        <svg viewBox="0 0 24 24" fill="none" class="w-5 h-5">
          <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <div>
        <h1 class="daily-title">
          <template v-if="step === 'result' && userName">
            {{ userName }}님의 오늘의 운세
          </template>
          <template v-else>오늘의 운세</template>
        </h1>
        <p class="daily-date">{{ todayLabel }}</p>
      </div>
    </div>

    <!-- ── Step 1: 방법 선택 ──────────────────────────────────────────────── -->
    <div v-if="step === 'select'" class="select-wrap animate-fade-up">
      <!-- 일진 미리보기 -->
      <div class="card ilju-preview">
        <div class="ilju-inner">
          <div class="ilju-ganji">
            <span class="ganji ganji-char" :style="`color: ${elColor(STEM_EL[todayIlju.stem] ?? '')}`">
              {{ STEM_HANJA[todayIlju.stem] }}
            </span>
            <span class="ganji ganji-char" :style="`color: ${elColor(BRANCH_EL[todayIlju.branch] ?? '')}`">
              {{ BRANCH_HANJA[todayIlju.branch] }}
            </span>
          </div>
          <p class="ilju-desc fs-sub">오늘 일진으로 보는 나의 운세</p>
        </div>
        <img src="/daily-illust.webp" class="ilju-illust" alt="" />
      </div>

      <!-- 방법 선택 -->
      <div class="method-btns">
        <button class="btn-primary method-btn" @click="step = 'input'">
          직접 입력하기
        </button>
        <button class="method-btn-outline" @click="goProfile">
          저장된 프로필로 보기
        </button>
      </div>
    </div>

    <!-- ── Step 2a: 직접 입력 폼 ─────────────────────────────────────────── -->
    <div v-else-if="step === 'input'" class="input-wrap animate-fade-up">
      <p class="input-guide fs-sub">생년월일시를 입력하면 오늘의 운세를 계산해 드립니다.</p>

      <div class="relative">
        <ClientOnly>
          <SajuInputForm submit-label="오늘의 운세 보기" @submit="onFormSubmit" />
        </ClientOnly>
      </div>

      <!-- 오류 -->
      <p v-if="error" class="error-msg fs-label">{{ error }}</p>

      <!-- 로딩 오버레이 -->
      <div v-if="loading" class="loading-overlay">
        <LoadingSpinner />
        <p class="fs-sub" style="color:var(--text-muted);margin-top:12px;">운세 계산 중…</p>
      </div>
    </div>

    <!-- ── Step 2b: 프로필 선택 ──────────────────────────────────────────── -->
    <div v-else-if="step === 'profile'" class="profile-step animate-fade-up">
      <SajuProfileList
        :profiles="profiles"
        :prof-load="profLoad"
        :loading="loading"
        @select="onProfileSelect"
      />
      <p v-if="error" class="error-msg fs-label">{{ error }}</p>
    </div>

    <!-- ── Step 3: 결과 ───────────────────────────────────────────────────── -->
    <div v-else-if="step === 'result' && result" class="result-wrap animate-fade-up">
    <SajuDailyResultPanel :result="result">
      <template #actions>
        <div class="result-actions">
          <button class="btn-share" :disabled="shareState === 'loading'" @click="doShare">
            <svg viewBox="0 0 24 24" fill="none" class="share-icon">
              <circle cx="18" cy="5" r="3" stroke="currentColor" stroke-width="1.8"/>
              <circle cx="6" cy="12" r="3" stroke="currentColor" stroke-width="1.8"/>
              <circle cx="18" cy="19" r="3" stroke="currentColor" stroke-width="1.8"/>
              <path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <template v-if="shareState === 'loading'">링크 생성 중…</template>
            <template v-else-if="shareState === 'error'">오류 발생</template>
            <template v-else>공유하기</template>
          </button>
          <button
            v-if="fromDirectInput"
            class="btn-save-profile"
            :class="{ 'is-done': saveProfileState === 'done' }"
            :disabled="saveProfileDisabled"
            @click="saveProfile"
          >{{ saveProfileLabel }}</button>
          <button class="btn-secondary" @click="reset">다른 사람 운세 보기</button>
        </div>
      </template>
    </SajuDailyResultPanel>
    </div>

  </div>

  <!-- 공유 모달 -->
  <UiShareModal v-model:show="showShareModal" :url="shareUrl" />

  <!-- 로그인 유도 다이얼로그 -->
  <AppDialog
    v-model:show="showLoginDialog"
    title="로그인이 필요해요"
    desc="저장된 프로필은 로그인 후 이용할 수 있어요."
    cancel-text="취소"
  >
    <button
      class="btn-primary"
      style="width:100%"
      @click="goLogin"
    >
      로그인하러 가기
    </button>
  </AppDialog>
</template>

<style scoped>
.daily-wrap {
  max-width: 480px;
  margin: 0 auto;
  padding: 12px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 헤더 */
.daily-header {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding-top: 8px;
}
.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  background: var(--surface-1);
  color: var(--text-secondary);
  flex-shrink: 0;
  margin-top: 2px;
  cursor: pointer;
  transition: background 0.15s;
}
.back-btn:hover { background: var(--surface-2); }
.daily-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.daily-date {
  font-size: var(--fs-sub);
  color: var(--text-muted);
  margin-top: 3px;
}

/* 로딩 */
.center-state {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Step1: 선택 ── */
.select-wrap { display: flex; flex-direction: column; gap: 14px; }

.ilju-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px;
  overflow: hidden;
  position: relative;
}
.ilju-inner { display: flex; flex-direction: column; gap: 6px; }
.ilju-ganji { display: flex; gap: 0; font-family: var(--font-ganji); line-height: 1; }
.ganji-char {
  font-size: 52px;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.ilju-desc { color: var(--text-muted); }
.ilju-illust {
  width: 88px;
  height: 88px;
  border-radius: 12px;
  object-fit: cover;
  flex-shrink: 0;
  opacity: 0.9;
}

.method-btns {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.method-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 15px 20px;
  font-size: var(--fs-body);
  font-weight: 700;
  border-radius: 12px;
  cursor: pointer;
}
.method-btn-outline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px 20px;
  font-size: var(--fs-body);
  font-weight: 700;
  border-radius: 12px;
  border: 2px solid var(--accent);
  background: transparent;
  color: var(--accent);
  cursor: pointer;
  transition: background 0.15s;
}
.method-btn-outline:hover { background: color-mix(in srgb, var(--accent) 8%, transparent); }

/* ── Step2a: 입력 폼 ── */
.input-wrap { display: flex; flex-direction: column; gap: 10px; }
.input-guide { color: var(--text-muted); padding: 0 2px; }
.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

/* ── Step2b: 프로필 ── */
.profile-step { display: flex; flex-direction: column; gap: 10px; }

.error-msg {
  color: var(--color-bad);
  padding: 0 4px;
  font-weight: 600;
}

/* ── Step3: 결과 ── */
.result-wrap { display: flex; flex-direction: column; gap: 12px; }

/* 결과 하단 액션 */
.result-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 4px;
}
.btn-share {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 13px;
  border-radius: 10px;
  border: 2px solid var(--accent);
  background: transparent;
  color: var(--accent);
  font-size: var(--fs-body);
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-share:hover:not(:disabled) { background: color-mix(in srgb, var(--accent) 8%, transparent); }
.btn-share:disabled { opacity: 0.5; cursor: not-allowed; }
.share-icon { width: 18px; height: 18px; flex-shrink: 0; }



/* 프로필 저장 버튼 */
.btn-save-profile {
  width: 100%;
  padding: 13px;
  border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  color: var(--text-primary);
  font-size: var(--fs-body);
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-save-profile:hover:not(:disabled) { background: var(--surface-2); }
.btn-save-profile:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-save-profile.is-done { border-color: var(--color-good); color: var(--color-good); }

/* 다시 계산 버튼 */
.btn-secondary {
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  color: var(--text-secondary);
  font-size: var(--fs-body);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  margin-top: 4px;
}
.btn-secondary:hover { background: var(--surface-2); }

/* PC */
@media (min-width: 768px) {
  .daily-wrap {
    max-width: 960px;
    padding: 32px 40px 60px;
    gap: 20px;
  }
  .ganji-char { font-size: 64px; }
  .ilju-illust { width: 110px; height: 110px; }
  .method-grid { grid-template-columns: 1fr 1fr; gap: 14px; }
  .method-card { padding: 28px 20px; }
  .method-icon { font-size: 36px; }
  .info-row { grid-template-columns: 1fr 1fr; }

  /* PC: 2열 그리드 */
  .fortunes-list {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }
}
</style>
