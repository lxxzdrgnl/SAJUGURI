/**
 * 카테고리 레이블·아이콘·순서 상수 — Single Source of Truth
 *
 * 한줄 상담(question)과 오늘의 운세(daily)는 카테고리 체계가 다르므로 분리.
 */

import type { QuestionCategory } from '~/types/saju'

// ── 한줄 상담 카테고리 ─────────────────────────────────────────────────────

export const QUESTION_CATEGORY_LABELS: Record<QuestionCategory, string> = {
  career:  '직업·이직',
  love:    '연애·결혼',
  money:   '재물·투자',
  health:  '건강',
  general: '기타',
}

// ── 오늘의 운세 카테고리 ───────────────────────────────────────────────────

export const DAILY_CATEGORY_ICONS: Record<string, string> = {
  exam:    '📚',
  money:   '💰',
  love:    '💕',
  career:  '💼',
  health:  '🌿',
  social:  '🤝',
}

export const DAILY_CATEGORY_ORDER = ['exam', 'money', 'love', 'career', 'health', 'social'] as const
