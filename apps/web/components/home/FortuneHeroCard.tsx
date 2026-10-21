'use client'

import { useEffect, useState } from 'react'
import type { ProfileResponse } from '@sajuguri/api-client'
import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/navigation'
import Card from '@/components/ui/Card'
import { buttonClass } from '@/components/ui/Button'
import FortuneBannerClient from '@/components/fortune/FortuneBannerClient'
import { buildBirthKey, loadCachedStory } from '@/lib/fortune/cache'
import { summarizeStory, todayLocal, type FortuneSummary } from '@/lib/home/fortuneSummary'
import { webStorage } from '@/lib/storage'

/** 홈 히어로 — 오늘의 운세. 첫 렌더는 안 본 상태(SSR 일치), 마운트 후 캐시를 읽어 교체한다. */
export default function FortuneHeroCard({
  profiles,
  isLoggedIn,
}: {
  profiles: ProfileResponse[]
  isLoggedIn: boolean
}) {
  const t = useTranslations('home.hero')
  const [summary, setSummary] = useState<FortuneSummary>({ seen: false })

  const rep = profiles.find((p) => p.is_representative) ?? profiles[0] ?? null

  useEffect(() => {
    if (!rep) return
    let cancelled = false
    const birthKey = buildBirthKey({
      birth_date: rep.birth_date,
      birth_time: rep.birth_time,
      gender: rep.gender,
      calendar: rep.calendar,
      is_leap_month: rep.is_leap_month,
    })
    loadCachedStory(webStorage, birthKey, todayLocal())
      .then((story) => { if (!cancelled) setSummary(summarizeStory(story)) })
      .catch(() => {})
    return () => { cancelled = true }
  }, [rep])

  return (
    <Card tone="soft" className="p-5">
      <FortuneBannerClient profiles={profiles} isLoggedIn={isLoggedIn}>
        {summary.seen ? (
          <div className="flex items-center gap-4">
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-c-text-sub">{t('seenTitle')}</p>
              <p className="mt-1 font-display text-3xl font-extrabold">{summary.score}</p>
              <p className="mt-1 text-sm font-bold">{summary.headline}</p>
              <span className={`${buttonClass('secondary', 'sm')} mt-3`}>{t('again')}</span>
            </div>
            <img src="/mascot/fortune.png" alt="" width={88} height={88} className="h-22 w-22 shrink-0 object-contain" />
          </div>
        ) : (
          <div className="flex items-center gap-4">
            <div className="min-w-0 flex-1">
              <span className="inline-block rounded-pill bg-c-accent px-2.5 py-0.5 text-xs font-extrabold text-c-on-accent">
                {t('freeDaily')}
              </span>
              <p className="mt-2 font-display text-xl font-extrabold">{t('unseen')}</p>
              <span className={`${buttonClass('primary', 'md')} mt-3`}>{t('cta')}</span>
            </div>
            <div className="relative shrink-0">
              <span className="absolute -top-3 right-full mr-1 whitespace-nowrap rounded-card border border-c-line bg-c-surface px-2.5 py-1 text-xs font-bold">
                {t('bubble')}
              </span>
              <img src="/mascot/fortune.png" alt="" width={88} height={88} className="h-22 w-22 object-contain" />
            </div>
          </div>
        )}
      </FortuneBannerClient>
      {summary.seen && (
        <Link href="/chat" className="mt-3 inline-block text-sm font-bold underline">
          {t('toCounsel')}
        </Link>
      )}
    </Card>
  )
}
