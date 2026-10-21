import type { ReactNode } from 'react'

/**
 * 페이지 헤더 규칙 — 큼직한 제목 + 포인트색 바.
 * accent prop은 호환을 위해 유지하지만 새 디자인은 단일 포인트색(yellow)만 쓴다.
 */
export default function PageHeading({
  title,
  children,
}: {
  title: ReactNode
  accent?: 'orange' | 'teal' | 'yellow'
  children?: ReactNode
}) {
  return (
    <div>
      <h1 className="text-[22px] font-black leading-tight text-c-text">{title}</h1>
      <span className="mt-2 block h-1.5 w-12 rounded-full bg-c-accent" />
      {children}
    </div>
  )
}
