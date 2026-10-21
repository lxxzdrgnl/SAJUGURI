import { getTranslations } from 'next-intl/server'
import { currentUser, serverAuthApi } from '@/lib/serverAuth'
import { listSessions, listProfiles } from '@sajuguri/api-client'
import type { ChatSession, ProfileResponse } from '@sajuguri/api-client'
import Card from '@/components/ui/Card'
import { buttonClass } from '@/components/ui/Button'
import ChatListClient from '@/components/chat/ChatListClient'
import PageHeading from '@/components/ui/PageHeading'
import { firstParam, resolvePrefill } from '@/lib/chat/prefill'

// 백엔드 직결 URL — 서버 컴포넌트는 next.config rewrites를 안 탄다
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const GOOGLE_LOGIN_URL = `${API_URL}/api/auth/google?client=web`

interface Props {
  searchParams: Promise<{ topic?: string | string[]; q?: string | string[] }>
}

export default async function ChatPage({ searchParams }: Props) {
  const t = await getTranslations('chat')
  const tp = await getTranslations('products')
  const sp = await searchParams
  // 새 상담 첫 입력창 힌트 (?topic= 상품 상담 문구 > ?q= 문구) — 자동 전송 안 함
  const prefill = resolvePrefill(firstParam(sp.topic), firstParam(sp.q), (id) =>
    tp.has(`${id}.counselPrompt`) ? tp(`${id}.counselPrompt`) : null,
  )
  const user = await currentUser()

  if (!user) {
    return (
      <main className="-mx-4 -mb-8 -mt-2 min-h-[calc(100dvh-3.5rem)] px-4 pb-10 pt-4">
        <div className="mb-4">
          <PageHeading title={t('title')} accent="teal" />
        </div>
        <Card tone="soft" className="flex flex-col items-center gap-4 px-5 py-8 text-center">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/mascot.svg" alt="" width={72} height={72} />
          <p className="text-[15px] font-extrabold">{t('loginRequired')}</p>
          <p className="text-sm text-c-text-sub">{t('loginDesc')}</p>
          <a
            href={GOOGLE_LOGIN_URL}
            className={`${buttonClass('primary', 'md')} w-full`}
          >
            {t('loginWithGoogle')}
          </a>
        </Card>
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
    <main className="-mx-4 -mb-8 -mt-2 min-h-[calc(100dvh-3.5rem)] px-4 pb-10 pt-4">
      <ChatListClient sessions={sessions} profiles={profiles} prefill={prefill} />
    </main>
  )
}
