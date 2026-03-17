<script setup lang="ts">
import type { SajuCalcResponse } from '~/types/saju'

const route = useRoute()
const config = useRuntimeConfig()
const token = route.params.token as string

const currentUrl = ref('')

// SSR로 가져와야 카카오 크롤러가 동적 메타태그를 읽을 수 있음
const { data: shareData, error: shareError } = await useAsyncData(
  `share-${token}`,
  () => $fetch<{
    calc_snapshot: SajuCalcResponse
    birth_input: Record<string, unknown> | null
  }>(`${config.public.apiBase}/api/share/${token}`),
)

const result = computed(() => shareData.value?.calc_snapshot ?? null)
const birthInput = computed(() => shareData.value?.birth_input ?? null)
const pending = computed(() => !shareData.value && !shareError.value)
const fetchError = computed(() => !!shareError.value)

const personName = computed(() => (birthInput.value?.name as string) || '사주구리')

useSeoMeta({
  title:          () => `${personName.value}님의 사주 만세력 보러가기`,
  ogTitle:        () => `${personName.value}님의 사주 만세력 보러가기`,
  description:    () => `${personName.value}님의 사주 분석 결과를 확인해보세요.`,
  ogDescription:  () => `${personName.value}님의 사주 분석 결과를 확인해보세요.`,
  ogImage:        `${config.public.siteUrl}/onboarding-illust.png?v=2`,
  ogUrl:          `${config.public.siteUrl}/share/${token}`,
})

onMounted(() => {
  currentUrl.value = window.location.href
})

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
      <LoadingSpinner size="lg" />
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
      <SajuResultPanel
        :result="result"
        :input-summary="inputSummary"
        :birth-input="birthInput"
        :fixed-share-url="currentUrl"
      >
        <!-- 나도 확인해보기 CTA -->
        <template #actions>
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
        </template>
      </SajuResultPanel>
    </div>

  </div>
</template>

<style scoped>
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
</style>
