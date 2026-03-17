<script setup lang="ts">
import type { ConsultationDetail } from '~/types/saju'

const route = useRoute()
const config = useRuntimeConfig()

const CATEGORY_LABELS: Record<string, string> = {
  career: '직업·이직',
  love:   '연애·결혼',
  money:  '재물·투자',
  health: '건강',
  general: '기타',
}

const token = route.params.token as string

const { data: item, error: fetchError } = await useAsyncData<ConsultationDetail>(
  `question-share-${token}`,
  () => $fetch<ConsultationDetail>(`${config.public.apiBase}/api/question/share/${token}`),
)

const personName = computed(() => item.value?.name || null)
const ogTitle = computed(() =>
  personName.value ? `${personName.value}님의 한줄상담 결과보기` : '한줄상담 결과보기'
)
const ogDesc = computed(() => item.value?.question ?? '사주구리 AI 한줄 상담')

useSeoMeta({
  title:         () => `사주구리 | ${ogTitle.value}`,
  ogTitle:       () => ogTitle.value,
  description:   () => ogDesc.value,
  ogDescription: () => ogDesc.value,
  ogType:        'website',
})

const error = computed(() => !!fetchError.value)

function formatDate(iso: string) {
  const d = new Date(iso)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}
</script>

<template>
  <div class="share-wrap">

    <div class="s-header">
      <NuxtLink to="/" class="logo-link">사주구리</NuxtLink>
      <p class="s-sub fs-sub">한줄 상담 공유</p>
    </div>

    <div v-if="!item && !error" class="center-state">
      <LoadingSpinner size="lg" />
    </div>

    <div v-else-if="error" class="error-card card">
      <p class="fs-body" style="color:var(--text-muted);">유효하지 않은 공유 링크이거나 삭제된 상담입니다.</p>
      <NuxtLink to="/" class="btn-primary" style="margin-top:16px;max-width:200px;margin-inline:auto;">
        홈으로
      </NuxtLink>
    </div>

    <template v-else-if="item">
      <div class="result-card card">
        <div class="result-top">
          <span class="result-category fs-tiny">{{ CATEGORY_LABELS[item.category] ?? item.category }}</span>
          <span class="result-date fs-tiny">{{ formatDate(item.created_at) }}</span>
        </div>
        <h2 class="result-headline">{{ item.headline }}</h2>
        <p class="result-content">{{ item.content }}</p>
      </div>

      <div class="echo-card card" style="padding:14px 18px;">
        <p class="fs-tiny" style="color:var(--text-muted);">상담 고민</p>
        <p class="fs-sub" style="color:var(--text-secondary);margin-top:4px;">{{ item.question }}</p>
      </div>

      <NuxtLink to="/question" class="btn-primary cta-btn">
        나도 한줄 상담 받기
      </NuxtLink>
    </template>

  </div>
</template>

<style scoped>
.share-wrap {
  max-width: 480px;
  margin: 0 auto;
  padding: 20px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.s-header { text-align: center; padding: 16px 0 8px; }
.logo-link { font-size: 20px; font-weight: 800; color: var(--accent); text-decoration: none; }
.s-sub { color: var(--text-muted); margin-top: 4px; }
.center-state { min-height: 200px; display: flex; align-items: center; justify-content: center; }
.error-card { padding: 32px; text-align: center; display: flex; flex-direction: column; align-items: center; }
.result-card { padding: 28px 24px; display: flex; flex-direction: column; gap: 10px; }
.result-top { display: flex; justify-content: space-between; align-items: center; }
.result-category { color: var(--accent); font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.result-date { color: var(--text-muted); }
.result-headline { font-size: 20px; font-weight: 800; color: var(--text-primary); line-height: 1.4; letter-spacing: -0.02em; }
.result-content { font-size: var(--fs-body); color: var(--text-secondary); line-height: 1.75; white-space: pre-wrap; }
.cta-btn { display: block; text-align: center; text-decoration: none; padding: 15px; border-radius: 12px; font-weight: 700; }

@media (min-width: 768px) {
  .share-wrap { max-width: 960px; padding: 32px 40px 60px; }
}
</style>
