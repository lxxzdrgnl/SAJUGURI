'use client'

import { createContext, useContext, type ReactNode } from 'react'
import type { ProfileResponse } from '@sajuguri/api-client'

interface HomeViewer {
  profiles: ProfileResponse[]
  isLoggedIn: boolean
  /** 대표 만세력 — 열람 기록 집계용 */
  repProfile: ProfileResponse | null
}

const Ctx = createContext<HomeViewer>({ profiles: [], isLoggedIn: false, repProfile: null })

/** 홈의 상품 진입(ProductLink)이 만세력 선택 시트·열람 기록에 쓰는 보는 사람 정보 */
export function HomeViewerProvider({
  profiles,
  isLoggedIn,
  children,
}: {
  profiles: ProfileResponse[]
  isLoggedIn: boolean
  children: ReactNode
}) {
  const repProfile = profiles.find((p) => p.is_representative) ?? null
  return <Ctx.Provider value={{ profiles, isLoggedIn, repProfile }}>{children}</Ctx.Provider>
}

export function useHomeViewer(): HomeViewer {
  return useContext(Ctx)
}
