<script setup lang="ts">
import type { DailyFortuneResponse } from '~/types/saju'

const route  = useRoute()
const config = useRuntimeConfig()
const token  = route.params.token as string
const { getDailyShareInput, getDailyFortune } = useSajuApi()

const loading = ref(false)
const error   = ref('')
const result  = ref<DailyFortuneResponse | null>(null)

// ── 공유 입력값 (SSR — 카카오 크롤러용 메타태그) ─────────────────────────────
const { data: shareData, error: shareError } = await useAsyncData(
  `daily-share-${token}`,
  () => getDailyShareInput(token),
)

const userName = computed(() => {
  const name = shareData.value?.birth_input?.name as string | undefined
  return name || '공유된 사람'
})

// ── 운세 계산 (클라이언트) ────────────────────────────────────────────────────
onMounted(async () => {
  if (shareError.value || !shareData.value) {
    error.value = '공유 링크를 불러오지 못했습니다.'
    return
  }
  loading.value = true
  try {
    const b = shareData.value.birth_input
    result.value = await getDailyFortune({
      birth_date:      b.birth_date as string,
      birth_time:      (b.birth_time as string | null) ?? null,
      gender:          (b.gender as 'male' | 'female'),
      calendar:        (b.calendar as 'solar' | 'lunar') ?? 'solar',
      is_leap_month:   (b.is_leap_month as boolean) ?? false,
      birth_longitude: (b.birth_longitude as number | null) ?? undefined,
    })
  } catch {
    error.value = '운세를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})

// ── 날짜 ──────────────────────────────────────────────────────────────────────
const todayLabel = computed(() => {
  const d = new Date()
  const days = ['일','월','화','수','목','금','토']
  return `${d.getFullYear()}년 ${d.getMonth()+1}월 ${d.getDate()}일 (${days[d.getDay()]})`
})

// ── SEO ───────────────────────────────────────────────────────────────────────
useSeoMeta({
  title:         () => `${userName.value}님의 오늘의 운세 보러가기`,
  ogTitle:       () => `${userName.value}님의 오늘의 운세 보러가기`,
  description:   () => `${userName.value}님의 오늘 운세를 확인해보세요.`,
  ogDescription: () => `${userName.value}님의 오늘 운세를 확인해보세요.`,
  ogImage:       `${config.public.siteUrl}/onboarding-illust.png`,
  ogUrl:         `${config.public.siteUrl}/daily/share/${token}`,
})
</script>

<template>
  <div class="share-wrap">

    <!-- 헤더 -->
    <div class="share-header">
      <NuxtLink to="/daily" class="back-btn">
        <svg viewBox="0 0 24 24" fill="none" class="w-5 h-5">
          <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </NuxtLink>
      <div>
        <h1 class="share-title">
          <template v-if="!loading && result">{{ userName }}님의 오늘의 운세</template>
          <template v-else>오늘의 운세</template>
        </h1>
        <p class="share-date fs-sub">{{ todayLabel }}</p>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="loading || (!result && !error && !shareError)" class="center-state">
      <LoadingSpinner />
      <p class="fs-sub" style="color:var(--text-muted);margin-top:12px;">운세 계산 중…</p>
    </div>

    <!-- 에러 -->
    <div v-else-if="error || shareError" class="card" style="text-align:center;padding:32px;">
      <p class="fs-body" style="color:var(--color-bad);">{{ error || '공유 링크를 불러오지 못했습니다.' }}</p>
      <NuxtLink to="/daily" class="btn-primary" style="margin-top:16px;max-width:200px;margin-inline:auto;">
        내 운세 보기
      </NuxtLink>
    </div>

    <!-- 결과 -->
    <div v-else-if="result" class="animate-fade-up">
      <SajuDailyResultPanel :result="result">
        <template #actions>
          <div class="cta-card">
            <div class="cta-text">
              <p class="cta-title">내 운세도 궁금하다면?</p>
              <p class="cta-desc">생년월일시만 입력하면 오늘의 운세를 바로 확인할 수 있어요.</p>
            </div>
            <NuxtLink to="/daily" class="btn-primary cta-btn">
              내 운세 보기
            </NuxtLink>
          </div>
        </template>
      </SajuDailyResultPanel>
    </div>
  </div>
</template>

<style scoped>
.share-wrap {
  max-width: 480px;
  margin: 0 auto;
  padding: 12px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.share-header {
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
  flex-shrink: 0; margin-top: 2px;
}
.share-title {
  font-size: 22px; font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em; line-height: 1.2;
}
.share-date { color: var(--text-muted); margin-top: 3px; }
.center-state {
  min-height: 300px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.cta-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 28px;
  border-radius: 16px;
  border: 1px solid var(--border-default);
  background: var(--surface-1);
  margin-top: 16px;
}
.cta-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.cta-title { font-size: var(--fs-body); font-weight: 700; color: var(--text-primary); }
.cta-desc { font-size: var(--fs-sub); color: var(--text-muted); }
.cta-btn { display: inline-flex; align-items: center; white-space: nowrap; padding: 12px 20px; width: auto; flex-shrink: 0; }

@media (min-width: 768px) {
  .share-wrap { max-width: 960px; padding: 32px 40px 60px; gap: 20px; }
}
@media (max-width: 640px) {
  .cta-card { flex-direction: column; align-items: flex-start; }
  .cta-btn { width: 100%; justify-content: center; }
}
</style>
