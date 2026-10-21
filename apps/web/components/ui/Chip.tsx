import type { ReactNode } from 'react'

const VARIANT = {
  default: 'border-c-line bg-c-surface text-c-text',
  lucky: 'border-transparent bg-c-lucky-bg text-c-lucky-fg',       // 길신
  unlucky: 'border-transparent bg-c-unlucky-bg text-c-unlucky-fg', // 흉살
  yellow: 'border-transparent bg-c-accent text-c-on-accent',
} as const

/** 통일 칩 — 알약 + 1px 라인, 의미는 variant 틴트 */
export default function Chip({
  variant = 'default',
  children,
}: {
  variant?: keyof typeof VARIANT
  children: ReactNode
}) {
  return (
    <span
      className={`mb-2 mr-1.5 inline-block rounded-pill border px-2.5 py-1
        text-xs font-extrabold ${VARIANT[variant]}`}
    >
      {children}
    </span>
  )
}
