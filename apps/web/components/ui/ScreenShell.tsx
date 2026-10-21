import type { ReactNode } from 'react'

/**
 * 화면 셸 — 레이아웃(app/[locale]/layout.tsx)이 이미 좌우 패딩·640px 컬럼·배경(body)을 준다.
 * 여기선 헤더(3.5rem)와 레이아웃 상하 패딩(pt-2 + pb-8 = 2.5rem)을 뺀 최소 높이만 보장한다.
 * center: 인증 완료·404 같은 상태 화면용 수직·수평 가운데 정렬.
 */
export default function ScreenShell({
  className = '',
  center = false,
  children,
}: {
  className?: string
  center?: boolean
  children: ReactNode
}) {
  // center는 레이아웃의 상하 패딩을 상쇄해 뷰포트 전체 높이 기준으로 가운데에 둔다
  const base = center
    ? '-mb-8 -mt-2 min-h-[calc(100dvh-3.5rem)]'
    : 'min-h-[calc(100dvh-6rem)]'
  const c = center ? ' flex items-center justify-center' : ''
  return <main className={`${base}${c}${className ? ` ${className}` : ''}`}>{children}</main>
}
