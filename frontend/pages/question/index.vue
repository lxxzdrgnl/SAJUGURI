<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import type { SajuCalcRequest, ConsultationResponse, QuestionCategory } from '~/types/saju'
// QuestionCategory는 결과 표시용으로만 사용

const auth   = useAuthStore()
const config = useRuntimeConfig()
const base   = config.public.apiBase
const { askQuestion, createConsultationShare } = useSajuApi()
const goToLogin = useGoToLogin()

// ── 상태 ─────────────────────────────────────────────────────────────────────
type Step = 'select' | 'input' | 'profile' | 'question' | 'result'

interface ProfileItem {
  id: number; name: string; birth_date: string; birth_time: string | null
  calendar: string; gender: string; is_leap_month: boolean
  day_stem: string | null; day_stem_element: string | null
}

const CATEGORY_LABELS: Record<QuestionCategory, string> = {
  career: '직업·이직',
  love:   '연애·결혼',
  money:  '재물·투자',
  health: '건강',
  general: '기타',
}

const step             = ref<Step>('select')
const loading          = ref(false)
const error            = ref('')
const result           = ref<ConsultationResponse | null>(null)
const profiles         = ref<ProfileItem[]>([])
const profLoad         = ref(false)
const showLoginDialog  = ref(false)
const pendingBirthInput = ref<SajuCalcRequest | null>(null)
const pendingName      = ref('')
const shareLoading     = ref(false)
const shareCopied      = ref(false)

// 고민 입력
const question   = ref('')
const CHAR_MIN   = 10
const CHAR_MAX   = 100
const questionValid = computed(
  () => question.value.length >= CHAR_MIN && question.value.length <= CHAR_MAX
)

// ── 프로필 로드 ───────────────────────────────────────────────────────────────
async function loadProfiles() {
  if (!auth.isLoggedIn) return
  profLoad.value = true
  try {
    profiles.value = await auth.authFetch<ProfileItem[]>(`${base}/api/profiles`)
  } catch { profiles.value = [] }
  finally { profLoad.value = false }
}

function goProfile() {
  if (!auth.isLoggedIn) { showLoginDialog.value = true; return }
  loadProfiles()
  step.value = 'profile'
}

// ── 생년월일 확보 후 고민 입력 스텝으로 ──────────────────────────────────────
function onFormSubmit(req: SajuCalcRequest) {
  pendingBirthInput.value = req
  pendingName.value = req.name ?? ''
  step.value = 'question'
}

function onProfileSelect(p: ProfileItem) {
  pendingBirthInput.value = {
    birth_date:    p.birth_date,
    birth_time:    p.birth_time ?? undefined,
    gender:        p.gender as 'male' | 'female',
    calendar:      p.calendar as 'solar' | 'lunar',
    is_leap_month: p.is_leap_month,
  }
  pendingName.value = p.name
  step.value = 'question'
}

// ── 상담 실행 ──────────────────────────────────────────────────────────────
async function submitQuestion() {
  if (!pendingBirthInput.value || !questionValid.value) return
  loading.value = true
  error.value   = ''
  try {
    result.value = await askQuestion({
      ...pendingBirthInput.value,
      question: question.value,
    }, auth.token)
    step.value = 'result'
  } catch {
    error.value = '상담을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    loading.value = false
  }
}

function reset() {
  result.value           = null
  error.value            = ''
  question.value         = ''
  pendingBirthInput.value = null
  pendingName.value      = ''
  shareLoading.value     = false
  shareCopied.value      = false
  step.value             = 'select'
}

async function shareResult() {
  if (!result.value) return
  shareLoading.value = true
  shareCopied.value  = false
  try {
    const { share_token } = await createConsultationShare(result.value.id, auth.token)
    const url = `${window.location.origin}/question/share/${share_token}`
    await navigator.clipboard.writeText(url)
    shareCopied.value = true
    setTimeout(() => { shareCopied.value = false }, 3000)
  } catch {
    // 공유 실패 시 조용히 무시
  } finally {
    shareLoading.value = false
  }
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
      <div v-if="profLoad" class="center-state"><LoadingSpinner size="sm" /></div>
      <div v-else-if="profiles.length === 0" class="card" style="text-align:center;padding:32px;">
        <p class="fs-body" style="color:var(--text-muted);">저장된 만세력이 없습니다.</p>
        <NuxtLink to="/profile" class="btn-primary" style="margin-top:16px;max-width:200px;margin-inline:auto;">
          만세력 보러가기
        </NuxtLink>
      </div>
      <div v-else class="profiles-list">
        <button
          v-for="p in profiles" :key="p.id"
          class="profile-card-item"
          :disabled="loading"
          @click="onProfileSelect(p)"
        >
          <div class="profile-card-inner">
            <div class="profile-info">
              <p class="profile-name">{{ p.name }}</p>
              <p class="profile-birth">
                {{ p.birth_date.replace(/-/g, '.') }} · {{ p.gender === 'male' ? '남' : '여' }}
              </p>
            </div>
          </div>
        </button>
      </div>
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
      <div class="result-card card">
        <p class="result-category fs-tiny">{{ CATEGORY_LABELS[result.category as QuestionCategory] ?? result.category }}</p>
        <h2 class="result-headline">{{ result.headline }}</h2>
        <p class="result-content">{{ result.content }}</p>
      </div>
      <div class="result-question-echo card" style="padding:14px 18px;">
        <p class="fs-tiny" style="color:var(--text-muted);">입력한 고민</p>
        <p class="fs-sub" style="color:var(--text-secondary);margin-top:4px;">{{ question }}</p>
      </div>
      <div class="result-actions">
        <button
          class="btn-share"
          :disabled="shareLoading"
          @click="shareResult"
        >
          <span v-if="shareCopied">링크 복사됨 ✓</span>
          <span v-else-if="shareLoading">생성 중…</span>
          <span v-else>공유하기</span>
        </button>
        <NuxtLink v-if="auth.isLoggedIn" to="/question/history" class="btn-history-link fs-label">
          내 상담 기록 보기
        </NuxtLink>
      </div>
      <button class="btn-secondary" @click="reset">다른 고민 상담하기</button>
    </div>

  </div>

  <!-- 로그인 유도 -->
  <AppDialog
    v-model:show="showLoginDialog"
    title="로그인이 필요해요"
    desc="저장된 만세력은 로그인 후 이용할 수 있어요."
    cancel-text="취소"
  >
    <button class="btn-primary" style="width:100%" @click="goToLogin()">로그인하러 가기</button>
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
.center-state { min-height: 200px; display: flex; align-items: center; justify-content: center; }
.profile-step { display: flex; flex-direction: column; gap: 10px; }
.profiles-list { display: flex; flex-direction: column; gap: 10px; }
.profile-card-item {
  border-radius: 16px; border: 1px solid var(--border-default);
  background: var(--surface-1); width: 100%; text-align: left;
  cursor: pointer; transition: background 0.15s;
}
.profile-card-item:hover:not(:disabled) { background: var(--surface-2); }
.profile-card-inner { padding: 18px 20px; }
.profile-name { font-size: 16px; font-weight: 700; color: var(--text-primary); }
.profile-birth { font-size: var(--fs-sub); color: var(--text-muted); margin-top: 4px; }

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
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.btn-share {
  flex: 1; padding: 11px 18px; border-radius: 10px;
  border: 1px solid var(--accent); background: transparent;
  color: var(--accent); font-size: var(--fs-label); font-weight: 700;
  cursor: pointer; transition: background 0.15s;
}
.btn-share:hover:not(:disabled) { background: color-mix(in srgb, var(--accent) 8%, transparent); }
.btn-share:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-history-link {
  padding: 11px 16px; border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--surface-1); color: var(--text-secondary);
  font-weight: 600; text-decoration: none; white-space: nowrap;
  transition: background 0.15s;
}
.btn-history-link:hover { background: var(--surface-2); }
.result-card { padding: 28px 24px; display: flex; flex-direction: column; gap: 12px; }
.result-category {
  color: var(--accent); font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em;
}
.result-headline {
  font-size: 20px; font-weight: 800; color: var(--text-primary);
  line-height: 1.4; letter-spacing: -0.02em;
}
.result-content {
  font-size: var(--fs-body); color: var(--text-secondary);
  line-height: 1.75; white-space: pre-wrap;
}
.btn-secondary {
  width: 100%; padding: 12px; border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--surface-1); color: var(--text-secondary);
  font-size: var(--fs-body); font-weight: 600; cursor: pointer;
  transition: background 0.15s;
}
.btn-secondary:hover { background: var(--surface-2); }

@media (min-width: 768px) {
  .question-wrap { max-width: 960px; padding: 32px 40px 60px; }
}
</style>
