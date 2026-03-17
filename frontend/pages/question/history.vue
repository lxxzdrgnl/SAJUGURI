<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import type { ConsultationHistoryItem } from '~/types/saju'

const auth = useAuthStore()
const { listConsultations, createConsultationShare, deleteConsultation } = useSajuApi()

const CATEGORY_LABELS: Record<string, string> = {
  career:  '직업·이직',
  love:    '연애·결혼',
  money:   '재물·투자',
  health:  '건강',
  general: '기타',
}

const items      = ref<ConsultationHistoryItem[]>([])
const loading    = ref(true)
const visible    = ref<Set<number>>(new Set())
const expanded   = ref<number | null>(null)
const copyStates = ref<Record<number, 'idle' | 'loading' | 'done'>>({})
const deleting   = ref<Set<number>>(new Set())
const fadeOut    = ref<Set<number>>(new Set())

async function load() {
  loading.value = true
  visible.value = new Set()
  expanded.value = null
  try {
    items.value = await listConsultations(auth.token as string)
    items.value.forEach((item, i) => {
      setTimeout(() => {
        visible.value = new Set([...visible.value, item.id])
      }, i * 80)
    })
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

function toggle(id: number) {
  expanded.value = expanded.value === id ? null : id
}

async function copyShare(item: ConsultationHistoryItem) {
  copyStates.value[item.id] = 'loading'
  try {
    let shareToken = item.share_token
    if (!shareToken) {
      const res = await createConsultationShare(item.id, auth.token as string)
      shareToken = res.share_token
      item.share_token = shareToken
    }
    await navigator.clipboard.writeText(`${window.location.origin}/question/share/${shareToken}`)
    copyStates.value[item.id] = 'done'
    setTimeout(() => { copyStates.value[item.id] = 'idle' }, 3000)
  } catch {
    copyStates.value[item.id] = 'idle'
  }
}

async function remove(item: ConsultationHistoryItem) {
  if (deleting.value.has(item.id)) return
  deleting.value = new Set([...deleting.value, item.id])
  try {
    await deleteConsultation(item.id, auth.token as string)
    fadeOut.value = new Set([...fadeOut.value, item.id])
    if (expanded.value === item.id) expanded.value = null
    setTimeout(() => {
      items.value = items.value.filter(i => i.id !== item.id)
      fadeOut.value.delete(item.id)
      deleting.value.delete(item.id)
    }, 300)
  } catch {
    deleting.value.delete(item.id)
  }
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  if (!auth.isLoggedIn) { navigateTo('/login'); return }
  load()
})
</script>

<template>
  <div class="history-wrap">

    <div class="h-header">
      <NuxtLink to="/question" class="back-btn" aria-label="뒤로">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </NuxtLink>
      <div>
        <h1 class="h-title">상담 목록</h1>
      </div>
    </div>

    <div v-if="loading" class="center-state">
      <LoadingSpinner size="lg" />
    </div>

    <div v-else-if="items.length === 0" class="empty-state card">
      <p class="fs-body" style="color:var(--text-muted);">아직 상담 기록이 없습니다.</p>
      <NuxtLink to="/question" class="btn-primary" style="margin-top:16px;max-width:200px;margin-inline:auto;">
        한줄 상담 받기
      </NuxtLink>
    </div>

    <div v-else class="items-list">
      <div
        v-for="item in items"
        :key="item.id"
        class="item-card card"
        :class="{
          'item-visible':   visible.has(item.id),
          'item-fade-out':  fadeOut.has(item.id),
          'item-expanded':  expanded === item.id,
        }"
      >
        <!-- 클릭 가능한 상단 요약 -->
        <button class="item-summary" @click="toggle(item.id)">
          <div class="item-meta">
            <span class="item-category fs-tiny">{{ CATEGORY_LABELS[item.category] ?? item.category }}</span>
            <span class="item-date fs-tiny">{{ formatDate(item.created_at) }}</span>
          </div>
          <p class="item-headline">{{ item.headline }}</p>
          <p class="item-question fs-sub">{{ item.question }}</p>
          <span class="chevron" :class="{ 'chevron-open': expanded === item.id }">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
        </button>

        <!-- 펼쳐지는 상세 내용 -->
        <div class="item-detail" :class="{ 'detail-open': expanded === item.id }">
          <div class="detail-inner">
            <div class="detail-divider" />
            <p class="detail-content">{{ item.content }}</p>
            <div class="item-actions">
              <button
                class="action-btn fs-label"
                :disabled="copyStates[item.id] === 'loading'"
                @click.stop="copyShare(item)"
              >
                <span v-if="copyStates[item.id] === 'done'">링크 복사됨 ✓</span>
                <span v-else-if="copyStates[item.id] === 'loading'">생성 중…</span>
                <span v-else>공유</span>
              </button>
              <button
                class="action-btn action-btn-delete fs-label"
                :disabled="deleting.has(item.id)"
                @click.stop="remove(item)"
              >
                {{ deleting.has(item.id) ? '삭제 중…' : '삭제' }}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
.history-wrap {
  max-width: 480px;
  margin: 0 auto;
  padding: 12px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.h-header { display: flex; align-items: flex-start; gap: 8px; padding-top: 8px; }
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 8px;
  border: 1px solid var(--border-subtle); background: var(--surface-1);
  color: var(--text-secondary); flex-shrink: 0; margin-top: 2px;
  text-decoration: none; transition: background 0.15s;
}
.back-btn:hover { background: var(--surface-2); }
.back-btn svg { width: 18px; height: 18px; }
.h-title { font-size: 22px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.02em; }
.h-subtitle { font-size: var(--fs-sub); color: var(--text-muted); margin-top: 3px; }

.center-state { min-height: 200px; display: flex; align-items: center; justify-content: center; }
.empty-state { padding: 32px; text-align: center; display: flex; flex-direction: column; align-items: center; }

/* 리스트 */
.items-list { display: flex; flex-direction: column; gap: 10px; }

/* 카드 페이드인 */
.item-card {
  padding: 0;
  overflow: hidden;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.35s ease, transform 0.35s ease, box-shadow 0.2s;
}
.item-card.item-visible { opacity: 1; transform: translateY(0); }
.item-card.item-fade-out {
  opacity: 0; transform: translateY(-6px);
  transition: opacity 0.3s ease, transform 0.3s ease;
  pointer-events: none;
}
.item-card.item-expanded {
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

/* 요약 (버튼) */
.item-summary {
  width: 100%; padding: 18px 20px;
  display: flex; flex-direction: column; gap: 5px;
  background: none; border: none; cursor: pointer;
  text-align: left; position: relative;
  transition: background 0.15s;
}
.item-summary:hover { background: var(--surface-2); }

.item-meta { display: flex; justify-content: space-between; align-items: center; }
.item-category { color: var(--accent); font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.item-date { color: var(--text-muted); }
.item-headline {
  font-size: 15px; font-weight: 700;
  color: var(--text-primary); line-height: 1.4;
  padding-right: 28px; /* chevron 공간 */
}
.item-question { font-size: var(--fs-sub); color: var(--text-muted); line-height: 1.5; }

.chevron {
  position: absolute; right: 18px; top: 50%;
  transform: translateY(-50%);
  display: flex; align-items: center;
  color: var(--text-muted);
  transition: transform 0.25s ease;
}
.chevron svg { width: 18px; height: 18px; }
.chevron.chevron-open { transform: translateY(-50%) rotate(180deg); }

/* 상세 펼침 — max-height 트릭으로 animate */
.item-detail {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.35s ease;
}
.item-detail.detail-open { max-height: 600px; }

.detail-inner { padding: 0 20px 18px; display: flex; flex-direction: column; gap: 12px; }
.detail-divider { height: 1px; background: var(--border-subtle); margin-bottom: 2px; }
.detail-content {
  font-size: var(--fs-body); color: var(--text-secondary);
  line-height: 1.75; white-space: pre-wrap;
}

.item-actions { display: flex; gap: 8px; }
.action-btn {
  padding: 6px 14px; border-radius: 8px;
  border: 1px solid var(--border-default); background: var(--surface-1);
  color: var(--text-secondary); font-weight: 600; cursor: pointer;
  transition: background 0.15s;
}
.action-btn:hover:not(:disabled) { background: var(--surface-2); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn-delete {
  color: #c04838;
  border-color: color-mix(in srgb, #c04838 30%, transparent);
}
.action-btn-delete:hover:not(:disabled) {
  background: color-mix(in srgb, #c04838 8%, transparent);
}

@media (min-width: 768px) {
  .history-wrap { max-width: 960px; padding: 32px 40px 60px; }
}
</style>
