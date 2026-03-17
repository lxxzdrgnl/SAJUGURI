<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import type { SajuCalcRequest, ConsultationResponse, QuestionCategory, ProfileResponse } from '~/types/saju'
import { STORAGE_KEYS } from '~/utils/storageKeys'
import { QUESTION_CATEGORY_LABELS as CATEGORY_LABELS } from '~/utils/category'

const auth   = useAuthStore()
const { askQuestion, createConsultationShare, getProfiles } = useSajuApi()
const goToLogin = useGoToLogin()

// ── 상태 ─────────────────────────────────────────────────────────────────────
type Step = 'select' | 'input' | 'profile' | 'question' | 'result'


const step              = ref<Step>('select')
const result            = ref<ConsultationResponse | null>(null)
const profiles          = ref<ProfileResponse[]>([])
const showLoginDialog   = ref(false)

const { loading,              error, run: runSubmit   } = useAsync()
const { loading: profLoad,          run: runProfiles  } = useAsync()
const pendingBirthInput = ref<SajuCalcRequest | null>(null)
const pendingName       = ref('')
const shareLoading         = ref(false)
const shareUrl             = ref('')
const fromDirectInput      = ref(false)
const showLoginPromoDialog = ref(false)
const showShareDialog      = ref(false)

// 고민 입력
const question   = ref('')
const CHAR_MIN   = 10
const CHAR_MAX   = 100
const questionValid = computed(
  () => question.value.length >= CHAR_MIN && question.value.length <= CHAR_MAX
)

// ── 프로필 저장 ───────────────────────────────────────────────────────────────
const { saveState: saveProfileState, saveProfile: _saveProfile, saveLabel: saveProfileLabel, saveDisabled: saveProfileDisabled } = useProfileSave()

async function saveProfile() {
  if (!auth.isLoggedIn) { showLoginDialog.value = true; return }
  if (!pendingBirthInput.value) return
  const b = pendingBirthInput.value
  await _saveProfile({
    name:          (b.name as string)?.trim() || pendingName.value || '내 사주',
    birth_date:    b.birth_date,
    birth_time:    b.birth_time ?? null,
    calendar:      b.calendar ?? 'solar',
    gender:        b.gender,
    is_leap_month: b.is_leap_month ?? false,
    city:          b.city ?? null,
    longitude:     b.birth_longitude ?? null,
  })
}

// ── 로그인 이동 시 자동 저장 → 복귀 시 자동 복원 ──────────────────────────────
useLoginStatePersist(
  STORAGE_KEYS.QUESTION_PENDING_INPUT,
  () => pendingBirthInput.value
    ? { birthInput: pendingBirthInput.value, result: result.value, name: pendingName.value, question: question.value, fromDirect: fromDirectInput.value }
    : null,
  ({ birthInput, result: savedResult, name, question: savedQuestion, fromDirect }) => {
    pendingBirthInput.value = birthInput
    pendingName.value       = name || ''
    question.value          = savedQuestion || ''
    fromDirectInput.value   = fromDirect ?? true
    if (savedResult) {
      result.value = savedResult
      step.value   = 'result'
    } else if (savedQuestion && birthInput) {
      submitQuestion()
    } else {
      step.value = 'question'
    }
  },
)

// ── 프로필 로드 ───────────────────────────────────────────────────────────────
async function loadProfiles() {
  if (!auth.isLoggedIn) return
  profiles.value = (await runProfiles(() => getProfiles(auth.token as string))) ?? []
}

function goProfile() {
  if (!auth.isLoggedIn) { showLoginDialog.value = true; return }
  loadProfiles()
  step.value = 'profile'
}

// ── 생년월일 확보 후 고민 입력 스텝으로 ──────────────────────────────────────
function onFormSubmit(req: SajuCalcRequest) {
  fromDirectInput.value   = true
  pendingBirthInput.value = req
  pendingName.value       = req.name ?? ''
  step.value              = 'question'
}

function onProfileSelect(p: ProfileResponse) {
  fromDirectInput.value   = false
  pendingBirthInput.value = {
    birth_date:    p.birth_date,
    birth_time:    p.birth_time ?? undefined,
    gender:        p.gender as 'male' | 'female',
    calendar:      p.calendar as 'solar' | 'lunar',
    is_leap_month: p.is_leap_month,
  }
  pendingName.value = p.name
  step.value        = 'question'
}

// ── 상담 실행 ──────────────────────────────────────────────────────────────
async function submitQuestion() {
  if (!pendingBirthInput.value || !questionValid.value) return
  const r = await runSubmit(
    () => askQuestion({
      ...pendingBirthInput.value!,
      name: pendingBirthInput.value!.name?.trim() || pendingName.value?.trim() || undefined,
      question: question.value,
    }, auth.token),
    '상담을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.',
  )
  if (r) {
    result.value = r
    step.value   = 'result'
    if (!auth.isLoggedIn) showLoginPromoDialog.value = true
  }
}

function reset() {
  result.value            = null
  error.value             = ''
  question.value          = ''
  pendingBirthInput.value = null
  pendingName.value       = ''
  shareLoading.value      = false
  shareUrl.value          = ''
  fromDirectInput.value   = false
  saveProfileState.value  = 'idle'
  step.value              = 'select'
}

async function shareResult() {
  if (!result.value) return

  if (!shareUrl.value) {
    shareLoading.value = true
    try {
      const { share_token } = await createConsultationShare(result.value.id, auth.token)
      shareUrl.value = `${window.location.origin}/question/share/${share_token}`
    } catch {
      return
    } finally {
      shareLoading.value = false
    }
  }

  showShareDialog.value = true
}
</script>

<template>
  <div class="question-wrap">

    <!-- 헤더 -->
    <div class="q-header">
      <button class="back-btn" @click="
        step === 'select' ? navigateTo('/')
        : step === 'result' ? reset()
        : step === 'question' ? (step = 'select')
        : (step = 'select')
      ">
        <svg viewBox="0 0 24 24" fill="none" class="w-5 h-5">
          <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <div>
        <h1 class="q-title">
          <template v-if="step === 'result' && pendingName">{{ pendingName }}님의 상담 결과</template>
          <template v-else>한줄 상담</template>
        </h1>
        <p class="q-subtitle">사주를 바탕으로 고민에 답해드립니다</p>
      </div>
    </div>

    <!-- ── Step 1: 방법 선택 ── -->
    <div v-if="step === 'select'" class="select-wrap animate-fade-up">
      <div class="intro-card card">
        <p class="intro-text">생년월일을 알면 고민에 대한<br>사주 기반 답변을 드립니다.</p>
      </div>
      <div class="method-btns">
        <button class="btn-primary method-btn" @click="step = 'input'">직접 입력하기</button>
        <button class="method-btn-outline" @click="goProfile">저장된 만세력으로 보기</button>
      </div>
    </div>

    <!-- ── Step 2a: 직접 입력 ── -->
    <div v-else-if="step === 'input'" class="input-wrap animate-fade-up">
      <ClientOnly>
        <SajuInputForm submit-label="다음" @submit="onFormSubmit" />
      </ClientOnly>
    </div>

    <!-- ── Step 2b: 프로필 선택 ── -->
    <div v-else-if="step === 'profile'" class="profile-step animate-fade-up">
      <SajuProfileList
        :profiles="profiles"
        :prof-load="profLoad"
        :loading="loading"
        @select="onProfileSelect"
      />
    </div>

    <!-- ── 로딩 ── -->
    <div v-else-if="step === 'question' && loading" class="loading-step animate-fade-up">
      <LoadingSpinner size="lg" />
      <p class="loading-msg">사주 보는 중…</p>
      <p class="loading-sub">{{ pendingName || '나' }}님의 팔자를 읽고 있습니다</p>
    </div>

    <!-- ── Step 3: 고민 입력 ── -->
    <div v-else-if="step === 'question' && !loading" class="question-step animate-fade-up">
      <p class="q-guide fs-sub">
        <strong>{{ pendingName || '나' }}</strong>의 고민을 입력해 주세요.
      </p>

      <!-- 고민 textarea -->
      <div class="textarea-wrap">
        <textarea
          v-model="question"
          class="question-textarea"
          :placeholder="`예: 올해 이직 운이 있을까요?\n예: 지금 만나는 사람과 궁합이 어떨까요?`"
          :maxlength="CHAR_MAX"
          rows="4"
        />
        <span
          class="char-count fs-tiny"
          :class="{ warn: question.length < CHAR_MIN && question.length > 0, ok: questionValid }"
        >{{ question.length }} / {{ CHAR_MAX }}</span>
      </div>
      <p v-if="question.length > 0 && question.length < CHAR_MIN" class="hint-text fs-tiny">
        최소 {{ CHAR_MIN }}자 이상 입력해 주세요.
      </p>

      <p v-if="error" class="error-msg fs-label">{{ error }}</p>

      <button
        class="btn-primary submit-btn"
        :disabled="!questionValid || loading"
        @click="submitQuestion"
      >
        <LoadingSpinner v-if="loading" size="sm" />
        <span v-else>상담 받기</span>
      </button>
    </div>

    <!-- ── Step 4: 결과 ── -->
    <div v-else-if="step === 'result' && result" class="result-wrap animate-fade-up">
      <QuestionConsultationResult
        :question="question"
        :headline="result.headline"
        :content="result.content"
        :category="result.category"
        :name="pendingName || null"
        :birth-date="pendingBirthInput?.birth_date ?? null"
        :birth-time="pendingBirthInput?.birth_time ?? null"
        :gender="pendingBirthInput?.gender ?? null"
      />
      <div class="result-actions">
        <button
          class="btn-share"
          :disabled="shareLoading"
          @click="shareResult"
        >
          <span v-if="shareLoading">생성 중…</span>
          <span v-else>공유하기</span>
        </button>
        <button class="btn-secondary" @click="reset">다른 고민 상담하기</button>
      </div>
      <template v-if="!auth.isLoggedIn || fromDirectInput">
        <p class="save-profile-hint fs-tiny">다음에도 이 프로필로 상담하고 싶다면?</p>
        <button
          class="btn-save-profile"
          :class="{ 'is-done': saveProfileState === 'done' }"
          :disabled="saveProfileDisabled"
          @click="saveProfile"
        >{{ saveProfileLabel }}</button>
      </template>
    </div>

  </div>

  <!-- 로그인 유도 (프로필 접근 시) -->
  <AppDialog
    v-model:show="showLoginDialog"
    title="로그인이 필요해요"
    desc="저장된 만세력은 로그인 후 이용할 수 있어요."
    cancel-text="취소"
  >
    <button class="btn-primary" style="width:100%" @click="goToLogin()">로그인하러 가기</button>
  </AppDialog>

  <!-- 공유 모달 -->
  <UiShareModal v-model:show="showShareDialog" :url="shareUrl" />

  <!-- 로그인 프로모 (결과 확인 후 비로그인) -->
  <AppDialog
    v-model:show="showLoginPromoDialog"
    title="매번 입력하기 번거로우시죠?"
    desc="로그인하면 만세력을 저장해두고 바로 불러올 수 있어요."
    cancel-text="괜찮아요"
  >
    <button class="btn-primary" style="width:100%" @click="goToLogin()">로그인하고 만세력 저장하기</button>
  </AppDialog>
</template>

<style scoped>
.question-wrap {
  max-width: 480px;
  margin: 0 auto;
  padding: 12px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.q-header {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding-top: 8px;
}
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  background: var(--surface-1);
  color: var(--text-secondary);
  flex-shrink: 0; margin-top: 2px; cursor: pointer;
  transition: background 0.15s;
}
.back-btn:hover { background: var(--surface-2); }
.q-title {
  font-size: 22px; font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em; line-height: 1.2;
}
.q-subtitle { font-size: var(--fs-sub); color: var(--text-muted); margin-top: 3px; }

/* Step1 */
.select-wrap { display: flex; flex-direction: column; gap: 14px; }
.intro-card { padding: 24px; text-align: center; }
.intro-text { font-size: var(--fs-body); color: var(--text-secondary); line-height: 1.7; }
.method-btns { display: flex; flex-direction: column; gap: 10px; }
.method-btn {
  width: 100%; padding: 15px; font-size: var(--fs-body);
  font-weight: 700; border-radius: 12px; cursor: pointer;
}
.method-btn-outline {
  width: 100%; padding: 14px; font-size: var(--fs-body);
  font-weight: 700; border-radius: 12px;
  border: 2px solid var(--accent); background: transparent;
  color: var(--accent); cursor: pointer; transition: background 0.15s;
}
.method-btn-outline:hover { background: color-mix(in srgb, var(--accent) 8%, transparent); }

/* Step2b */
.profile-step { display: flex; flex-direction: column; gap: 10px; }

/* 로딩 */
.loading-step {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  min-height: 240px; gap: 14px;
}
.loading-msg {
  font-size: 18px; font-weight: 800;
  color: var(--text-primary); letter-spacing: -0.02em;
}
.loading-sub { font-size: var(--fs-sub); color: var(--text-muted); }

/* Step3 — 고민 입력 */
.question-step { display: flex; flex-direction: column; gap: 12px; }
.q-guide { color: var(--text-muted); }
.category-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.cat-chip {
  padding: 6px 14px; border-radius: 20px;
  border: 1px solid var(--border-default);
  background: var(--surface-1); color: var(--text-secondary);
  font-size: var(--fs-label); font-weight: 600; cursor: pointer;
  transition: all 0.15s;
}
.cat-chip.active {
  border-color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, transparent);
  color: var(--accent);
}
.textarea-wrap { position: relative; }
.question-textarea {
  width: 100%; min-height: 100px; padding: 14px 16px;
  border-radius: 12px; border: 1px solid var(--border-default);
  background: var(--surface-1); color: var(--text-primary);
  font-size: var(--fs-body); font-family: inherit; resize: vertical;
  transition: border-color 0.15s; box-sizing: border-box;
}
.question-textarea:focus { outline: none; border-color: var(--accent); }
.char-count {
  position: absolute; bottom: 10px; right: 14px;
  color: var(--text-muted);
}
.char-count.warn { color: var(--color-bad); }
.char-count.ok   { color: var(--text-muted); }
.hint-text { color: var(--text-muted); padding: 0 4px; }
.submit-btn {
  width: 100%; padding: 15px; font-size: var(--fs-body);
  font-weight: 700; border-radius: 12px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.error-msg { color: var(--color-bad); font-weight: 600; }

/* Step4 — 결과 */
.result-wrap { display: flex; flex-direction: column; gap: 12px; }
.result-actions {
  display: flex; flex-direction: column; gap: 10px;
}
.btn-share {
  flex: 1; padding: 13px 18px; border-radius: 10px;
  border: none; background: var(--accent);
  color: #fff; font-size: var(--fs-body); font-weight: 700;
  cursor: pointer; transition: opacity 0.15s;
}
.btn-share:hover:not(:disabled) { opacity: 0.88; }
.btn-share:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary {
  width: 100%; padding: 12px; border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--surface-1); color: var(--text-secondary);
  font-size: var(--fs-body); font-weight: 600; cursor: pointer;
  transition: background 0.15s;
}
.btn-secondary:hover { background: var(--surface-2); }
.save-profile-hint {
  color: var(--text-muted); text-align: left; font-size: 13px; margin-bottom: -4px;
}
.btn-save-profile {
  width: 100%; padding: 12px; border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--surface-1); color: var(--text-secondary);
  font-size: var(--fs-body); font-weight: 600;
  cursor: pointer; transition: background 0.15s;
}
.btn-save-profile:hover:not(:disabled) { background: var(--surface-2); }
.btn-save-profile:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-save-profile.is-done { color: var(--accent); border-color: var(--accent); }

@media (min-width: 768px) {
  .question-wrap { max-width: 960px; padding: 32px 40px 60px; }
}
</style>
