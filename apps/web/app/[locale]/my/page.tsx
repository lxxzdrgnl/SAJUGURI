import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { currentUser, serverAuthApi } from '@/lib/serverAuth'
import { maskEmail } from '@/lib/mask'
import Card from '@/components/ui/Card'
import { buttonClass } from '@/components/ui/Button'
import MascotTinted from '@/components/ui/MascotTinted'
import MyRecordsClient from '@/components/my/MyRecordsClient'
import { listProfiles } from '@sajuguri/api-client'
import type { ProfileResponse } from '@sajuguri/api-client'
import { fetchAllRecords } from '@/lib/records/registry'

// 브라우저가 직접 여는 풀 URL — next.config rewrites를 타지 않도록 백엔드 절대 주소 사용.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const GOOGLE_LOGIN_URL = `${API_URL}/api/auth/google?client=web`

/** 날짜 문자열(YYYY-MM-DD) → 한국식 날짜 표기 */
function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default async function MyPage() {
  const t = await getTranslations('my')
  const user = await currentUser()

  if (!user) {
    return (
      <main className="-mx-4 -mt-2 -mb-8 flex min-h-[calc(100dvh-3.5rem)] flex-col gap-5 px-4 pb-8 pt-4">
        <h1 className="font-display text-xl font-normal text-c-text">{t('title')}</h1>
        <Card className="flex flex-col items-center gap-4 py-8 text-center">
          <MascotTinted width={72} height={72} />
          <p className="text-[15px] font-extrabold text-c-text">{t('loginRequired')}</p>
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

  // 저장 만세력
  let profiles: ProfileResponse[] = []
  try {
    profiles = await listProfiles(authApi)
  } catch {
    profiles = []
  }

  // 대표 만세력
  const repProfile = profiles.find((p) => p.is_representative) ?? null

  // 내 기록 — 레코드 레지스트리로 모든 종류 병렬 fetch (개별 실패는 빈 배열)
  const records = await fetchAllRecords(authApi)

  return (
    <main className="-mx-4 -mt-2 -mb-8 flex min-h-[calc(100dvh-3.5rem)] flex-col gap-5 px-4 pb-8 pt-4">
      {/* ── 상단 히어로: 대표 만세력 카드 (이메일 포함) ─── */}
      <section>
        {repProfile ? (
          <div className="rounded-card bg-c-poster-butter p-4">
            <div className="flex items-center gap-3">
              <span className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-card bg-c-surface">
                <MascotTinted stem={repProfile.day_stem} width={72} height={72} />
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-[18px] font-black leading-tight text-c-text">{repProfile.name}</p>
                {repProfile.day_stem && repProfile.day_branch && (
                  <p className="mt-0.5 text-[13px] font-extrabold text-c-text">
                    {repProfile.day_stem}{repProfile.day_branch}일주
                  </p>
                )}
                <p className="mt-1 text-[12px] font-semibold text-c-text-sub">
                  {t('repCard.born')} {formatDate(repProfile.birth_date)}
                </p>
                <p className="mt-1 text-[11px] text-c-text-sub">{maskEmail(user.email)}</p>
              </div>
              <span className="shrink-0 self-start rounded-pill bg-c-surface px-3 py-1 text-[12px] font-extrabold text-c-text">
                {t('repCard.badge')}
              </span>
            </div>
          </div>
        ) : (
          <Card tone="soft" className="flex flex-col items-center gap-3 py-6 text-center">
            <MascotTinted width={56} height={56} />
            <div>
              <p className="text-[14px] font-extrabold text-c-text">
                {t('repCard.noProfile')}
              </p>
              <p className="mt-1 text-[12px] text-c-text-sub">{t('repCard.noProfileDesc')}</p>
            </div>
            <Link
              href="/manse"
              className={buttonClass('primary', 'md')}
            >
              {t('repCard.goManse')}
            </Link>
            <p className="text-[11px] text-c-text-sub">
              {maskEmail(user.email)}
            </p>
          </Card>
        )}
      </section>

      {/* ── 내 기록: 리포트 / 운세 탭 + 더보기 + 삭제 ─── */}
      <MyRecordsClient records={records} repProfileName={repProfile?.name ?? null} />

      {/* 언어·로그아웃은 ≡ 드로어에서 */}
    </main>
  )
}
