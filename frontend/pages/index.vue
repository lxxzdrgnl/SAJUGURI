<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useSajuStore } from '~/stores/saju'
import type { SajuCalcRequest, DailyFortuneResponse } from '~/types/saju'
import {
  STEM_HANJA, BRANCH_HANJA, STEM_COLOR, STEM_ELEMENT, BRANCH_ELEMENT, BRANCH_ANIMAL,
  KOREAN_DAYS, iljuColor, stemLabelColor, formatIljuHanja, formatIljuLabel,
} from '~/utils/ganji'

interface ProfileItem {
  id: number
  name: string
  birth_date: string
  birth_time: string | null
  calendar: string
  gender: string
  is_leap_month: boolean
  city: string | null
  longitude: number | null
  is_representative: boolean
  day_stem: string | null
  day_branch: string | null
  day_stem_element: string | null
}

const auth = useAuthStore()
const config = useRuntimeConfig()
const base = config.public.apiBase

const pending = ref(true)
const repProfile = ref<ProfileItem | null>(null)
const dailyOverall = ref<string | null>(null)
const { getDailyFortune } = useSajuApi()

// ── 오늘의 일진 계산 ──
const todayIlju = computed(() => {
  const today = new Date()
  const base = new Date(1900, 0, 1)
  const days = Math.floor((today.getTime() - base.getTime()) / 86400000)
  const stemIdx = ((days % 10) + 10) % 10
  const branchIdx = ((days + 10) % 12 + 12) % 12
  const stem = ['갑','을','병','정','무','기','경','신','임','계'][stemIdx]
  const branch = ['자','축','인','묘','진','사','오','미','신','유','술','해'][branchIdx]
  return {
    stem,
    branch,
    stemHanja: STEM_HANJA[stem],
    branchHanja: BRANCH_HANJA[branch],
    element: STEM_ELEMENT[stem],
    branchElement: BRANCH_ELEMENT[branch],
    animal: BRANCH_ANIMAL[branch],
    colorLabel: STEM_COLOR[stem],
    date: today,
  }
})

const todayLabel = computed(() => {
  const d = todayIlju.value.date
  return `${d.getFullYear()}년 ${d.getMonth()+1}월 ${d.getDate()}일 (${KOREAN_DAYS[d.getDay()]})`
})

onMounted(async () => {
  if (!auth.isLoggedIn) {
    pending.value = false
    return
  }
  try {
    const p = await auth.authFetch<ProfileItem>(`${base}/api/profiles/representative`)
    repProfile.value = p
    // 한줄 운세 — 백그라운드로 조용히 로드
    getDailyFortune({
      birth_date:      p.birth_date,
      birth_time:      p.birth_time,
      gender:          p.gender as 'male' | 'female',
      calendar:        p.calendar as 'solar' | 'lunar',
      is_leap_month:   p.is_leap_month,
      birth_longitude: p.longitude ?? undefined,
    }).then((r: DailyFortuneResponse) => { dailyOverall.value = r.overall }).catch(() => {})
  } catch {
    // 404 or error — 온보딩 화면 표시
  } finally {
    pending.value = false
  }
})

const iljuHanja = computed(() => formatIljuHanja(repProfile.value?.day_stem, repProfile.value?.day_branch))
const iljuLabel = computed(() => formatIljuLabel(repProfile.value?.day_stem, repProfile.value?.day_branch))

const birthLabel = computed(() => {
  if (!repProfile.value) return ''
  const [y, m, d] = repProfile.value.birth_date.split('-')
  const cal = repProfile.value.calendar === 'lunar' ? '음력' : '양력'
  return `${y}년 ${m}월 ${d}일 (${cal})`
})

const hasProfile = computed(() => !!repProfile.value)

const store = useSajuStore()

function goToMyProfile() {
  const p = repProfile.value
  if (!p) return
  const req: SajuCalcRequest = {
    name:           p.name,
    birth_date:     p.birth_date,
    birth_time:     p.birth_time,
    gender:         p.gender as 'male' | 'female',
    calendar:       p.calendar as 'solar' | 'lunar',
    is_leap_month:  p.is_leap_month,
    city:           p.city ?? undefined,
    birth_longitude: p.longitude ?? undefined,
  }
  store.calculate(req)   // await 없이 — profile 페이지가 loading 스피너 처리
  navigateTo('/profile')
}
</script>

<template>
  <div class="home-wrap">


    <!-- 로딩 -->
    <div v-if="pending" class="loading-state">
      <LoadingSpinner />
    </div>

    <div v-else-if="!pending" class="dashboard animate-fade-up">

      <!-- 왼쪽: 일진 + 프로필 or 온보딩 -->
      <div class="dashboard-left">
        <!-- 프로필 카드 (있을 때만) -->
        <button v-if="hasProfile" class="profile-card animate-fade-up" @click="goToMyProfile">
          <div class="profile-card-inner">
            <div class="profile-info">
              <p class="profile-name">
                {{ repProfile!.name }}
                <span
                  v-if="repProfile!.day_stem"
                  class="profile-name-ilju"
                  :style="`color: ${iljuColor(repProfile!.day_stem_element)}`"
                >
                  ({{ iljuHanja }})
                </span>
              </p>
              <p class="profile-birth">{{ birthLabel }}</p>
              <p v-if="repProfile!.day_stem" class="profile-ilju">
                <span
                  class="ilju-value"
                  :style="`color: ${iljuColor(repProfile!.day_stem_element)}`"
                >{{ iljuLabel }}</span>
              </p>
            </div>
            <div class="profile-illust-mini">
              <img src="/profile-illust.webp" alt="" />
            </div>
          </div>
        </button>

        <!-- 프로필 없을 때 온보딩 -->
        <div v-else class="onboarding-inline animate-fade-up">
          <div class="illust-box">
            <img src="/onboarding-illust.webp" alt="사주 일러스트" class="illust-img" />
          </div>
          <p class="onboarding-title">아직 프로필이 없으시네요</p>
          <p class="onboarding-desc">생년월일시만 알면 내 사주 프로필 바로 만들 수 있어요.</p>
          <NuxtLink to="/profile" class="btn-primary onboarding-btn">
            만세력 보러가기
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none">
              <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </NuxtLink>
        </div>

        <!-- 오늘의 일진 카드 -->
        <div class="ilijn-card animate-fade-up animate-delay-100">
          <div class="ilijn-header">
            <span class="ilijn-label">오늘의 일진</span>
            <span class="ilijn-date">{{ todayLabel }}</span>
          </div>
          <div class="ilijn-body">
            <div class="ilijn-ganji">
              <span class="ilijn-stem" :style="`color: ${iljuColor(todayIlju.element)}`">{{ todayIlju.stemHanja }}</span>
              <span class="ilijn-branch" :style="`color: ${iljuColor(todayIlju.branchElement)}`">{{ todayIlju.branchHanja }}</span>
            </div>
            <div class="ilijn-divider" />
            <div class="ilijn-desc">
              <div class="ilijn-desc-row">
                <span :style="`color: ${stemLabelColor(todayIlju.colorLabel)}`" class="ilijn-desc-val">{{ todayIlju.colorLabel }}</span>
                <span class="ilijn-desc-dot">·</span>
                <span :style="`color: ${stemLabelColor(todayIlju.colorLabel)}`" class="ilijn-desc-val">{{ todayIlju.animal }}</span>
              </div>
              <div class="ilijn-badges">
                <span class="ilijn-element-badge" :style="`color: ${iljuColor(todayIlju.element)}; border-color: ${iljuColor(todayIlju.element)}`">천간 {{ todayIlju.element }}</span>
                <span class="ilijn-element-badge" :style="`color: ${iljuColor(todayIlju.branchElement)}; border-color: ${iljuColor(todayIlju.branchElement)}`">지지 {{ todayIlju.branchElement }}</span>
              </div>
            </div>
          </div>
          <!-- 한줄 운세 (대표 프로필 있을 때) -->
          <div v-if="hasProfile" class="ilijn-fortune">
            <p class="ilijn-fortune-text" :class="{ 'ilijn-fortune-loading': !dailyOverall }">
              {{ dailyOverall ?? '운세 불러오는 중…' }}
            </p>
            <NuxtLink to="/daily" class="ilijn-fortune-link">
              오늘의 운세 자세히 보기
              <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- 오른쪽: 서비스 목록 -->
      <div class="dashboard-right animate-fade-up animate-delay-200">
        <p class="service-label">서비스</p>
        <div class="service-grid">
          <NuxtLink to="/profile" class="service-card">
            <div class="service-card-img-wrap">
              <img src="/home-illust.webp" alt="만세력" class="service-card-img" />
            </div>
            <div class="service-card-footer">
              <div>
                <p class="service-name">만세력</p>
                <p class="service-desc">4기둥·오행·대운 정밀 분석</p>
              </div>
              <svg class="service-arrow" viewBox="0 0 24 24" fill="none">
                <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </NuxtLink>

          <NuxtLink to="/daily" class="service-card service-card-daily">
            <div class="service-card-img-wrap">
              <img src="/daily-illust.webp" alt="오늘의 운세" class="service-card-img" />
            </div>
            <div class="service-card-footer">
              <div>
                <p class="service-name">오늘의 운세</p>
                <p class="service-desc">시험·재물·연애·건강 6가지 분석</p>
              </div>
              <svg class="service-arrow" viewBox="0 0 24 24" fill="none">
                <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </NuxtLink>

          <NuxtLink to="/question" class="service-card service-card-question">
            <div class="service-card-img-wrap">
              <img src="/question-illust.webp" alt="한줄 상담" class="service-card-img service-card-img--question" />
            </div>
            <div class="service-card-footer">
              <div>
                <p class="service-name">한줄 상담</p>
                <p class="service-desc">사주 기반 고민 AI 단답 상담</p>
              </div>
              <svg class="service-arrow" viewBox="0 0 24 24" fill="none">
                <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </NuxtLink>
        </div>
      </div>

    </div>

  </div>
</template>

<style scoped>
.home-wrap {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  padding: 12px 20px 40px;
  max-width: 480px;
  margin: 0 auto;
}

.loading-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── 온보딩 인라인 ── */
.onboarding-inline {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 8px 0 4px;
}
.illust-box {
  width: 220px;
  height: 220px;
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  margin-bottom: 8px;
}
.illust-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.3);
}
.onboarding-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
}
.onboarding-desc {
  font-size: var(--fs-sub);
  color: var(--text-muted);
  text-align: center;
  line-height: 1.6;
}
.onboarding-btn {
  margin-top: 8px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 14px 28px;
  font-size: var(--fs-body);
  width: auto;
}

/* ── 대시보드 ── */
.dashboard {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-top: 12px;
}
.dashboard-left,
.dashboard-right {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ── PC 레이아웃 ── */
@media (min-width: 768px) {
  .home-wrap {
    max-width: 960px;
    padding: 32px 40px 60px;
  }
  .dashboard {
    flex-direction: row;
    align-items: flex-start;
    gap: 32px;
  }
  .dashboard-left {
    flex: 1;
    min-width: 0;
  }
  .dashboard-right {
    flex: 1;
    min-width: 0;
  }
  .onboarding-inline {
    border: 1px solid var(--border-default);
    border-radius: 20px;
    padding: 40px 32px;
    background: var(--surface-1);
    gap: 14px;
  }
  .illust-box {
    width: 260px;
    height: 260px;
    margin-bottom: 4px;
  }
}

.profile-card {
  border-radius: 20px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  overflow: hidden;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}
.profile-card:hover { background: var(--surface-2); }
.profile-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 24px 28px;
  gap: 16px;
}
.profile-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.profile-illust-mini {
  width: 88px;
  height: 88px;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--surface-2);
}
.profile-illust-mini img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.profile-name {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}
.profile-name-ilju {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-토, #8b5e30);
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
  gap: 8px;
  margin-top: 4px;
}
.ilju-label {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 6px;
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
  letter-spacing: 0.02em;
}
.ilju-value {
  font-size: 18px;
  font-weight: 700;
  font-family: var(--font-ganji);
  letter-spacing: 0.05em;
}
.ilju-animal {
  font-size: var(--fs-sub);
  color: var(--text-secondary);
}

/* ── 서비스 ── */
.service-label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  text-transform: uppercase;
  padding-left: 4px;
}
.service-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
.service-card {
  display: flex;
  flex-direction: column;
  border-radius: 20px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  text-decoration: none;
  overflow: hidden;
  transition: background 0.15s;
}
.service-card:hover {
  background: var(--surface-2);
}
.service-card-img-wrap {
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
}
.service-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.service-card-img--question {
  transform: scale(1.06);
  transform-origin: 32% center;
  object-position: 32% center;
}
.service-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-top: 1px solid var(--border-subtle);
  gap: 12px;
}
.service-name {
  font-size: var(--fs-body);
  font-weight: 700;
  color: var(--text-primary);
}
.service-desc {
  font-size: var(--fs-sub);
  color: var(--text-muted);
  margin-top: 2px;
}
.service-arrow {
  width: 18px;
  height: 18px;
  color: var(--text-muted);
  flex-shrink: 0;
}

/* ── 오늘의 일진 카드 ── */
.ilijn-card {
  order: -1; /* 모바일: 프로필/온보딩보다 위 */
  border-radius: 20px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.ilijn-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.ilijn-label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.ilijn-date {
  font-size: var(--fs-sub);
  color: var(--text-muted);
}
.ilijn-body {
  display: flex;
  align-items: center;
  gap: 24px;
}
.ilijn-ganji {
  display: flex;
  gap: 2px;
  font-family: var(--font-ganji);
  line-height: 1;
  flex-shrink: 0;
}
.ilijn-stem,
.ilijn-branch {
  font-size: 52px;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.ilijn-divider {
  width: 1px;
  height: 48px;
  background: var(--border-subtle);
  flex-shrink: 0;
}
.ilijn-desc {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}
.ilijn-desc-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--fs-body);
  font-weight: 700;
}
.ilijn-desc-dot {
  color: var(--border-default);
}
.ilijn-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.ilijn-element-badge {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.03em;
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid;
}

/* ── PC 일진/프로필 카드 ── */
@media (min-width: 768px) {
  .ilijn-card {
    order: 0; /* PC: 프로필 아래 */
    padding: 28px 32px;
    gap: 20px;
  }
  .ilijn-stem,
  .ilijn-branch {
    font-size: 72px;
  }
  .ilijn-divider {
    height: 64px;
  }
  .ilijn-desc-row {
    font-size: var(--fs-section);
  }
  .ilijn-element-badge {
    font-size: 12px;
    padding: 3px 10px;
  }
  .profile-card-inner {
    padding: 32px 28px;
    gap: 24px;
  }
  .profile-illust-mini {
    width: 110px;
    height: 110px;
    border-radius: 20px;
  }
  .profile-name {
    font-size: 26px;
  }
  .profile-name-ilju {
    font-size: 18px;
  }
  .ilju-value {
    font-size: 22px;
  }
  .service-card-img-wrap {
    aspect-ratio: 16 / 9;
  }
  .service-card-img--question {
    transform: scale(1.06);
    transform-origin: 32% center;
    object-position: 32% center;
  }
}
/* ── 한줄 운세 ── */
.ilijn-fortune {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
}
.ilijn-fortune-text {
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-secondary);
  margin: 0;
}
.ilijn-fortune-loading { color: var(--text-muted); }
.ilijn-fortune-link {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: var(--accent);
  text-decoration: none;
  width: fit-content;
}
.ilijn-fortune-link:hover { text-decoration: underline; }
</style>
