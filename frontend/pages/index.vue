<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

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

// ── 오늘의 일진 계산 ──
const STEMS = ['갑','을','병','정','무','기','경','신','임','계']
const BRANCHES = ['자','축','인','묘','진','사','오','미','신','유','술','해']
const STEM_ELEMENT: Record<string, string> = {
  '갑':'목','을':'목','병':'화','정':'화','무':'토',
  '기':'토','경':'금','신':'금','임':'수','계':'수',
}
const BRANCH_ELEMENT: Record<string, string> = {
  '자':'수','축':'토','인':'목','묘':'목','진':'토','사':'화',
  '오':'화','미':'토','신':'금','유':'금','술':'토','해':'수',
}

const todayIlju = computed(() => {
  const today = new Date()
  const base = new Date(1900, 0, 1)
  const days = Math.floor((today.getTime() - base.getTime()) / 86400000)
  const stemIdx = ((days % 10) + 10) % 10
  const branchIdx = ((days + 10) % 12 + 12) % 12
  const stem = STEMS[stemIdx]
  const branch = BRANCHES[branchIdx]
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
  const days = ['일','월','화','수','목','금','토']
  return `${d.getFullYear()}년 ${d.getMonth()+1}월 ${d.getDate()}일 (${days[d.getDay()]})`
})

onMounted(async () => {
  if (!auth.isLoggedIn) {
    pending.value = false
    return
  }
  try {
    repProfile.value = await $fetch<ProfileItem>(`${base}/api/profiles/representative`, {
      headers: { Authorization: `Bearer ${auth.token}` },
    })
  } catch {
    // 404 or error — 온보딩 화면 표시
  } finally {
    pending.value = false
  }
})

const STEM_HANJA: Record<string, string> = {
  '갑': '甲', '을': '乙', '병': '丙', '정': '丁', '무': '戊',
  '기': '己', '경': '庚', '신': '辛', '임': '壬', '계': '癸',
}
const BRANCH_HANJA: Record<string, string> = {
  '자': '子', '축': '丑', '인': '寅', '묘': '卯', '진': '辰', '사': '巳',
  '오': '午', '미': '未', '신': '申', '유': '酉', '술': '戌', '해': '亥',
}
const STEM_COLOR: Record<string, string> = {
  '갑': '청', '을': '청',
  '병': '붉은', '정': '붉은',
  '무': '황', '기': '황',
  '경': '흰', '신': '흰',
  '임': '검은', '계': '검은',
}
const BRANCH_ANIMAL: Record<string, string> = {
  '자': '쥐', '축': '소', '인': '호랑이', '묘': '토끼',
  '진': '용', '사': '뱀', '오': '말', '미': '양',
  '신': '원숭이', '유': '닭', '술': '개', '해': '돼지',
}

const iljuHanja = computed(() => {
  const p = repProfile.value
  if (!p?.day_stem || !p?.day_branch) return ''
  return `${STEM_HANJA[p.day_stem] ?? p.day_stem}${BRANCH_HANJA[p.day_branch] ?? p.day_branch}`
})

function iljuColor(element: string | null): string {
  if (!element) return 'var(--text-secondary)'
  if (element === '수') return '#888'
  return `var(--el-${element})`
}

const iljuLabel = computed(() => {
  const p = repProfile.value
  if (!p?.day_stem || !p?.day_branch) return ''
  return `${STEM_COLOR[p.day_stem] ?? p.day_stem} ${BRANCH_ANIMAL[p.day_branch] ?? p.day_branch}`
})

const birthLabel = computed(() => {
  if (!repProfile.value) return ''
  const [y, m, d] = repProfile.value.birth_date.split('-')
  const cal = repProfile.value.calendar === 'lunar' ? '음력' : '양력'
  return `${y}년 ${m}월 ${d}일 (${cal})`
})

const hasProfile = computed(() => !!repProfile.value)
</script>

<template>
  <div class="home-wrap">


    <!-- 로딩 -->
    <div v-if="pending" class="loading-state">
      <svg class="animate-spin w-8 h-8" viewBox="0 0 40 40" fill="none">
        <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
        <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
      </svg>
    </div>

    <div v-else-if="!pending" class="dashboard">

      <!-- 왼쪽: 일진 + 프로필 or 온보딩 -->
      <div class="dashboard-left">
        <!-- 프로필 카드 (있을 때만) -->
        <div v-if="hasProfile" class="profile-card">
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
              <img src="/profile-illust.jpg" alt="" />
            </div>
          </div>
        </div>

        <!-- 프로필 없을 때 온보딩 -->
        <div v-else class="onboarding-inline">
          <div class="illust-box">
            <img src="/onboarding-illust.png" alt="사주 일러스트" class="illust-img" />
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
        <div class="ilijn-card">
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
                <span :style="`color: ${iljuColor(todayIlju.element)}`" class="ilijn-desc-val">{{ todayIlju.colorLabel }}</span>
                <span class="ilijn-desc-dot">·</span>
                <span :style="`color: ${iljuColor(todayIlju.branchElement)}`" class="ilijn-desc-val">{{ todayIlju.animal }}</span>
              </div>
              <div class="ilijn-badges">
                <span class="ilijn-element-badge" :style="`color: ${iljuColor(todayIlju.element)}; border-color: ${iljuColor(todayIlju.element)}`">천간 {{ todayIlju.element }}</span>
                <span class="ilijn-element-badge" :style="`color: ${iljuColor(todayIlju.branchElement)}; border-color: ${iljuColor(todayIlju.branchElement)}`">지지 {{ todayIlju.branchElement }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 오른쪽: 서비스 목록 -->
      <div class="dashboard-right">
        <p class="service-label">서비스</p>
        <div class="service-grid">
          <NuxtLink to="/profile" class="service-card">
            <div class="service-card-img-wrap">
              <img src="/home-illust.png" alt="만세력" class="service-card-img" />
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
}
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
}
</style>
