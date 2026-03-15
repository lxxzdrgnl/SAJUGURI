<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import type { SajuCalcRequest, DailyFortuneResponse } from '~/types/saju'

const auth   = useAuthStore()
const config = useRuntimeConfig()
const base   = config.public.apiBase
const { getDailyFortune } = useSajuApi()

// ── 상수 ────────────────────────────────────────────────────────────────────
const STEMS    = ['갑','을','병','정','무','기','경','신','임','계']
const BRANCHES = ['자','축','인','묘','진','사','오','미','신','유','술','해']
const STEM_HANJA: Record<string,string> = {
  '갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊',
  '기':'己','경':'庚','신':'辛','임':'壬','계':'癸',
}
const BRANCH_HANJA: Record<string,string> = {
  '자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳',
  '오':'午','미':'未','신':'申','유':'酉','술':'戌','해':'亥',
}
const STEM_EL: Record<string,string> = {
  '갑':'목','을':'목','병':'화','정':'화','무':'토',
  '기':'토','경':'금','신':'금','임':'수','계':'수',
}
const BRANCH_EL: Record<string,string> = {
  '자':'수','축':'토','인':'목','묘':'목','진':'토','사':'화',
  '오':'화','미':'토','신':'금','유':'금','술':'토','해':'수',
}
const CAT_ICON: Record<string,string> = {
  exam:'📚', money:'💰', love:'💕', career:'💼', health:'🌿', social:'🤝',
}
const CAT_ORDER = ['exam','money','love','career','health','social']
const EL_SWATCH: Record<string,string> = {
  '목':'var(--el-목)', '화':'var(--el-화)', '토':'var(--el-토)',
  '금':'var(--el-금)', '수':'var(--el-수)',
}

// ── 상태 ────────────────────────────────────────────────────────────────────
type Step = 'select' | 'input' | 'profile' | 'result'

interface ProfileItem {
  id: number; name: string; birth_date: string; birth_time: string | null
  calendar: string; gender: string; is_leap_month: boolean
  day_stem: string | null; day_stem_element: string | null
}

const step            = ref<Step>('select')
const loading         = ref(false)
const error           = ref('')
const result          = ref<DailyFortuneResponse | null>(null)
const userName        = ref('')
const profiles        = ref<ProfileItem[]>([])
const profLoad        = ref(false)
const showLoginDialog = ref(false)
const fromDirectInput = ref(false)

// ── 프로필 저장 ──────────────────────────────────────────────────────────────
const { saveState: saveProfileState, saveProfile: _saveProfile, saveLabel: saveProfileLabel, saveDisabled: saveProfileDisabled } = useProfileSave()

async function saveProfile() {
  if (!auth.isLoggedIn) { showLoginDialog.value = true; return }
  if (!lastBirthInput.value) return
  const b = lastBirthInput.value
  const dp = result.value?.birth_day_pillar
  await _saveProfile({
    name:             (b.name as string)?.trim() || '내 사주',
    birth_date:       b.birth_date as string,
    birth_time:       (b.birth_time as string | null) ?? null,
    calendar:         (b.calendar as string) ?? 'solar',
    gender:           b.gender as string,
    is_leap_month:    (b.is_leap_month as boolean) ?? false,
    city:             (b.city as string | null) ?? null,
    longitude:        (b.birth_longitude as number | null) ?? null,
    day_stem:         dp?.stem ?? null,
    day_branch:       dp?.branch ?? null,
    day_stem_element: dp?.stem_element ?? null,
  })
}

// ── 공유 상태 ────────────────────────────────────────────────────────────────
const shareState    = ref<'idle' | 'loading' | 'error'>('idle')
const shareUrl      = ref('')
const showShareModal = ref(false)
const shareCopied   = ref(false)
const lastBirthInput = ref<Record<string, unknown> | null>(null)

const { createDailyShare } = useSajuApi()

async function doShare() {
  if (shareUrl.value) { showShareModal.value = true; return }
  if (!lastBirthInput.value) return
  shareState.value = 'loading'
  try {
    const data = await createDailyShare(lastBirthInput.value)
    shareUrl.value = data.share_url
    shareState.value = 'idle'
    showShareModal.value = true
  } catch {
    shareState.value = 'error'
    setTimeout(() => { shareState.value = 'idle' }, 2500)
  }
}

async function copyShareUrl() {
  await navigator.clipboard.writeText(shareUrl.value)
  shareCopied.value = true
  setTimeout(() => { shareCopied.value = false }, 2000)
}

// ── 오늘 날짜 ────────────────────────────────────────────────────────────────
const todayLabel = computed(() => {
  const d = new Date()
  const days = ['일','월','화','수','목','금','토']
  return `${d.getFullYear()}년 ${d.getMonth()+1}월 ${d.getDate()}일 (${days[d.getDay()]})`
})

const todayIlju = computed(() => {
  const today = new Date()
  const bdate = new Date(1900, 0, 1)
  const days = Math.floor((today.getTime() - bdate.getTime()) / 86400000)
  const stem   = STEMS[((days % 10) + 10) % 10]
  const branch = BRANCHES[((days + 10) % 12 + 12) % 12]
  return { stem, branch }
})

// ── 프로필 로드 ──────────────────────────────────────────────────────────────
async function loadProfiles() {
  if (!auth.isLoggedIn) return
  profLoad.value = true
  try {
    profiles.value = await auth.authFetch<ProfileItem[]>(`${base}/api/profiles`, {
    })
  } catch { profiles.value = [] }
  finally { profLoad.value = false }
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

function goLogin() {
  if (lastBirthInput.value) {
    localStorage.setItem('daily_pending_input', JSON.stringify(lastBirthInput.value))
  }
  goToLogin()
}

// ── 로그인 후 복원 ────────────────────────────────────────────────────────────
onMounted(() => {
  const pending = localStorage.getItem('daily_pending_input')
  if (pending) {
    localStorage.removeItem('daily_pending_input')
    try {
      const b = JSON.parse(pending)
      fromDirectInput.value = true
      calcFortune({
        birth_date:      b.birth_date,
        birth_time:      b.birth_time ?? null,
        gender:          b.gender,
        calendar:        b.calendar ?? 'solar',
        is_leap_month:   b.is_leap_month ?? false,
        birth_longitude: b.birth_longitude ?? undefined,
      }, b.name || '')
    } catch { /* ignore */ }
  }
})

// ── 계산 ────────────────────────────────────────────────────────────────────
async function calcFortune(req: SajuCalcRequest, name: string) {
  loading.value = true
  error.value   = ''
  userName.value = name || '나'
  shareUrl.value = ''   // 새 계산마다 공유 URL 초기화
  lastBirthInput.value = {
    name:           req.name ?? name,
    birth_date:     req.birth_date,
    birth_time:     req.birth_time ?? null,
    gender:         req.gender,
    calendar:       req.calendar ?? 'solar',
    is_leap_month:  req.is_leap_month ?? false,
    birth_longitude: req.birth_longitude ?? null,
  }
  try {
    result.value = await getDailyFortune({
      birth_date:    req.birth_date,
      birth_time:    req.birth_time,
      gender:        req.gender,
      calendar:      req.calendar,
      is_leap_month: req.is_leap_month,
      birth_longitude: req.birth_longitude,
    })
    step.value = 'result'
  } catch {
    error.value = '운세를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    loading.value = false
  }
}

function onFormSubmit(req: SajuCalcRequest) {
  fromDirectInput.value = true
  calcFortune(req, req.name ?? '')
}

function onProfileSelect(p: ProfileItem) {
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

// ── 색상 유틸 ────────────────────────────────────────────────────────────────
function elColor(el: string): string {
  if (!el) return 'var(--text-secondary)'
  if (el === '수') return '#888'
  return `var(--el-${el})`
}

function scoreColor(score: number): string {
  if (score >= 80) return 'var(--color-good)'
  if (score >= 60) return 'var(--accent)'
  if (score >= 45) return '#c07818'
  return 'var(--color-bad)'
}

// ── 결과 계산 ────────────────────────────────────────────────────────────────
const orderedFortunes = computed(() => {
  if (!result.value) return []
  return CAT_ORDER.map(k => ({ key: k, ...result.value!.fortunes[k] }))
})

const stemEl   = computed(() => result.value ? STEM_EL[result.value.day_ganji.stem]    ?? '' : '')
const branchEl = computed(() => result.value ? BRANCH_EL[result.value.day_ganji.branch] ?? '' : '')
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
        <img src="/daily-illust.png" class="ilju-illust" alt="" />
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
        <svg class="animate-spin w-8 h-8" viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
          <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
        </svg>
        <p class="fs-sub" style="color:var(--text-muted);margin-top:12px;">운세 계산 중…</p>
      </div>
    </div>

    <!-- ── Step 2b: 프로필 선택 ──────────────────────────────────────────── -->
    <div v-else-if="step === 'profile'" class="profile-step animate-fade-up">
      <div v-if="profLoad" class="center-state">
        <svg class="animate-spin w-7 h-7" viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
          <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
        </svg>
      </div>
      <div v-else-if="profiles.length === 0" class="card" style="text-align:center;padding:32px;">
        <p class="fs-body" style="color:var(--text-muted);">저장된 프로필이 없습니다.</p>
        <NuxtLink to="/profile" class="btn-primary" style="margin-top:16px;max-width:200px;margin-inline:auto;">
          만세력 보러가기
        </NuxtLink>
      </div>
      <div v-else class="profiles-list">
        <button
          v-for="p in profiles"
          :key="p.id"
          class="profile-card-item"
          :disabled="loading"
          @click="onProfileSelect(p)"
        >
          <div class="profile-card-inner">
            <div class="profile-info">
              <p class="profile-name">
                {{ p.name }}
                <span
                  v-if="p.day_stem"
                  class="profile-name-ilju"
                  :style="`color: ${elColor(p.day_stem_element ?? '')}`"
                >
                  ({{ STEM_HANJA[p.day_stem] ?? p.day_stem }})
                </span>
              </p>
              <p class="profile-birth">
                {{ p.birth_date.replace(/-/g, '.') }} · {{ p.gender === 'male' ? '남' : '여' }}
                <template v-if="p.birth_time"> · {{ p.birth_time }}</template>
              </p>
              <p v-if="p.day_stem" class="profile-ilju">
                <span class="ilju-value" :style="`color: ${elColor(p.day_stem_element ?? '')}`">
                  {{ STEM_HANJA[p.day_stem] ?? p.day_stem }}
                  {{ BRANCH_HANJA[(p as any).day_branch ?? ''] ?? '' }}
                </span>
              </p>
            </div>
            <div class="profile-illust-mini">
              <svg v-if="loading" class="animate-spin" viewBox="0 0 40 40" fill="none" style="width:28px;height:28px;">
                <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
                <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
              </svg>
              <img v-else src="/profile-illust.jpg" alt="" />
            </div>
          </div>
        </button>
      </div>
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
  <AppDialog
    v-model:show="showShareModal"
    title="오늘의 운세 공유"
    desc="링크를 열면 오늘 날짜 기준으로 재계산됩니다."
    cancel-text="닫기"
  >
    <div class="share-url-row">
      <span class="share-url-text fs-tiny">{{ shareUrl }}</span>
      <button class="share-copy-btn fs-label" @click="copyShareUrl">
        {{ shareCopied ? '복사됨!' : '복사' }}
      </button>
    </div>
  </AppDialog>

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
.profiles-list { display: flex; flex-direction: column; gap: 10px; }

.profile-card-item {
  border-radius: 20px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  overflow: hidden;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}
.profile-card-item:hover:not(:disabled) { background: var(--surface-2); }
.profile-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 20px 24px;
  gap: 16px;
}
.profile-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.profile-illust-mini {
  width: 72px;
  height: 72px;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
}
.profile-illust-mini img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.profile-name {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}
.profile-name-ilju {
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-ganji);
  letter-spacing: 0.03em;
}
.profile-birth {
  font-size: var(--fs-sub);
  color: var(--text-muted);
}
.profile-ilju {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}
.ilju-value {
  font-size: 16px;
  font-weight: 700;
  font-family: var(--font-ganji);
  letter-spacing: 0.05em;
}

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

/* 공유 URL 행 */
.share-url-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--surface-2);
  border: 1px solid var(--border-subtle);
  margin-top: 4px;
}
.share-url-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-secondary);
}
.share-copy-btn {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid var(--accent);
  background: transparent;
  color: var(--accent);
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.share-copy-btn:hover { background: color-mix(in srgb, var(--accent) 10%, transparent); }

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
