'use client'

import type { ReactNode } from 'react'
import { GOOGLE_LOGIN_URL, saveCurrentLocation } from '@/lib/loginReturn'

interface Props {
  className?: string
  children: ReactNode
}

/** 구글 로그인 링크 — 이동 직전에 지금 보던 화면을 저장해 로그인 후 돌아오게 한다 */
export default function GoogleLoginLink({ className, children }: Props) {
  return (
    <a href={GOOGLE_LOGIN_URL} className={className} onClick={saveCurrentLocation}>
      {children}
    </a>
  )
}
