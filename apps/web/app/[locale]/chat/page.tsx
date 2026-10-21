import { getTranslations } from 'next-intl/server'
import { currentUser, serverAuthApi } from '@/lib/serverAuth'
import { listSessions, listProfiles } from '@sajuguri/api-client'
import type { ChatSession, ProfileResponse } from '@sajuguri/api-client'
import BrutalCard from '@/components/ui/BrutalCard'
import ChatListClient from '@/components/chat/ChatListClient'
import PageHeading from '@/components/ui/PageHeading'
import { PRODUCTS } from '@sajuguri/core'

// 백엔드 직결 URL — 서버 컴포넌트는 next.config rewrites를 안 탄다
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const GOOGLE_LOGIN_URL = `${API_URL}/api/auth/google?client=web`

/** 첫 입력 힌트 최대 길이 — URL로 들어온 임의 문자열을 제한한다 */
const PREFILL_MAX = 500

/**
 * 새 상담 첫 입력창 힌트 — ?topic=<ProductId>면 그 상품의 상담 문구, 아니면 ?q=<문구>.
 * 자동 전송은 하지 않는다.
 */
async function resolvePrefill(topic?: string, q?: string): Promise<string | null> {
  if (topic && PRODUCTS.some((p) => p.id === topic)) {
    const tp = await getTranslations('products')
    const key = `${topic}.counselPrompt`
    if (tp.has(key)) return tp(key)
  }
  const text = q?.trim()
  return text ? text.slice(0, PREFILL_MAX) : null
}

interface Props {
  searchParams: Promise<{ topic?: string | string[]; q?: string | string[] }>
}

const first = (v?: string | string[]) => (Array.isArray(v) ? v[0] : v)

export default async function ChatPage({ searchParams }: Props) {
  const t = await getTranslations('chat')
  const sp = await searchParams
  const prefill = await resolvePrefill(first(sp.topic), first(sp.q))
  const user = await currentUser()

  if (!user) {
    return (
      <main>
        <div className="mb-4">
          <PageHeading title={t('title')} accent="teal" />
        </div>
        <BrutalCard className="flex flex-col items-center gap-4 py-8 text-center">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/mascot.svg" alt="" width={72} height={72} />
          <p className="text-[15px] font-extrabold">{t('loginRequired')}</p>
          <p className="text-sm text-text-sub">{t('loginDesc')}</p>
          <a
            href={GOOGLE_LOGIN_URL}
            className="w-full rounded-lg border-2 border-ink bg-yellow py-3 text-sm font-extrabold shadow-brutal text-center block"
          >
            {t('loginWithGoogle')}
          </a>
        </BrutalCard>
      </main>
    )
  }

  const authApi = await serverAuthApi()

  // 세션 목록 + 저장 만세력 (백엔드 미가동 시 빈 배열 fallback)
  let sessions: ChatSession[] = []
  let profiles: ProfileResponse[] = []

  await Promise.allSettled([
    listSessions(authApi).then((r) => { sessions = r }),
    listProfiles(authApi).then((r) => { profiles = r }),
  ])

  return (
    <main>
      <ChatListClient sessions={sessions} profiles={profiles} prefill={prefill} />
    </main>
  )
}
