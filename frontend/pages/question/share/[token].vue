<script setup lang="ts">
import type { ConsultationDetail } from '~/types/saju'
import { QUESTION_CATEGORY_LABELS as CATEGORY_LABELS } from '~/utils/category'

const route = useRoute()
const config = useRuntimeConfig()

const token = route.params.token as string

const { data: item, error: fetchError } = await useAsyncData<ConsultationDetail>(
  `question-share-${token}`,
  () => $fetch<ConsultationDetail>(`${config.public.apiBase}/api/question/share/${token}`),
)

const personName = computed(() => item.value?.name || null)
const bi = computed(() => item.value?.birth_input as Record<string, unknown> | null | undefined)
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
      <QuestionConsultationResult
        :question="item.question"
        :headline="item.headline"
        :content="item.content"
        :category="item.category"
        :name="personName"
        :birth-date="bi?.birth_date as string | null ?? null"
        :birth-time="bi?.birth_time as string | null ?? null"
        :gender="bi?.gender as string | null ?? null"
        :created-at="item.created_at"
      />

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
/* 고민 카드 */
.cta-btn { display: block; text-align: center; text-decoration: none; padding: 15px; border-radius: 12px; font-weight: 700; }

@media (min-width: 768px) {
  .share-wrap { max-width: 960px; padding: 32px 40px 60px; }
}
</style>
