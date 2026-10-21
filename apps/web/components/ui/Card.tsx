import type { HTMLAttributes } from 'react'

const TONE = {
  plain: 'bg-c-surface text-c-text border border-c-line',
  soft: 'bg-c-surface-soft text-c-text',
  counsel: 'bg-c-counsel-bg text-c-counsel-fg',
} as const

/** 카탈로그 카드 — 그림자 없음. plain=1px 라인, soft=무테, counsel=상담 강조 */
export default function Card({
  tone = 'plain',
  className = '',
  children,
  ...rest
}: { tone?: keyof typeof TONE } & HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`rounded-card ${TONE[tone]} ${className}`.trim()} {...rest}>
      {children}
    </div>
  )
}
