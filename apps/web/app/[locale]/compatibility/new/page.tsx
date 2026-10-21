'use client'

import { useState, useEffect } from 'react'
import { useTranslations, useLocale } from 'next-intl'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import type { ProfileResponse, BirthInput } from '@sajuguri/api-client'
import { api } from '@/lib/api'
import { createCompatibilityJob } from '@sajuguri/api-client'
import { useGenerationJob } from '@/lib/hooks/useGenerationJob'
import Card from '@/components/ui/Card'
import { buttonClass } from '@/components/ui/Button'
import PersonSlotPicker, { type PersonPick } from '@/components/compatibility/PersonSlotPicker'

export default function CompatibilityNewPage() {
  const t = useTranslations('compatibility')
  const locale = useLocale()
  const router = useRouter()

  const [profiles, setProfiles] = useState<ProfileResponse[]>([])
  const [topics, setTopics] = useState('')
  const [error, setError] = useState('')
  const [phraseIdx, setPhraseIdx] = useState(0)
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null)

  const { loading, error: jobError, start } = useGenerationJob((_type, resultId) => {
    router.replace(`/compatibility/${resultId}`)
  })

  const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
  const GOOGLE_LOGIN_URL = `${API_URL}/api/auth/google?client=web`

  const loadingPhrases = [
    t('new.loading.0'),
    t('new.loading.1'),
    t('new.loading.2'),
    t('new.loading.3'),
    t('new.loading.4'),
  ]

  // 로그인 상태 확인 + 프로필 로드
  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then((r) => (r.ok ? r.json() : null))
      .then((user) => {
        setIsLoggedIn(!!user)
        if (!user) return
        return fetch('/api/profiles', { credentials: 'include' })
          .then((r) => (r.ok ? r.json() : []))
          .then(setProfiles)
      })
      .catch(() => setIsLoggedIn(false))
  }, [])

  // 로딩 문구 순환
  useEffect(() => {
    if (!loading) return
    const timer = setInterval(() => {
      setPhraseIdx((i) => (i + 1) % loadingPhrases.length)
    }, 3000)
    return () => clearInterval(timer)
  }, [loading, loadingPhrases.length])

  function toBirthInput(pick: PersonPick): BirthInput {
    return {
      name: pick.name,
      birth_date: pick.birth_date,
      birth_time: pick.birth_time,
      gender: pick.gender,
      calendar: pick.calendar,
      is_leap_month: pick.is_leap_month,
      ...(pick.birth_longitude != null ? { birth_longitude: pick.birth_longitude } : {}),
    }
  }

  async function handleComplete(a: PersonPick, b: PersonPick) {
    setError('')
    try {
      const { job_id } = await createCompatibilityJob(api, {
        person_a: toBirthInput(a),
        person_b: toBirthInput(b),
        ...(topics.trim() ? { request_topics: topics.trim() } : {}),
        language: locale,
      })
      start(job_id)
    } catch (err: unknown) {
      const status = (err as { status?: number })?.status
      if (status === 401) {
        setError(t('new.errorLogin'))
      } else if (status === 429) {
        setError(t('new.errorLimit'))
      } else {
        setError(t('new.errorFallback'))
      }
    }
  }

  // 로딩 중 화면
  if (loading) {
    return (
      <main className="-mx-4 -mt-2 -mb-8 bg-c-bg px-4 pb-8 pt-4 shadow-[0_0_0_100vmax_var(--c-bg)] [clip-path:inset(0_-100vmax_-100vmax)] flex min-h-[70vh] flex-col items-center justify-center gap-6 text-center">
        <Image src="/mascot.svg" alt="" width={72} height={72} className="animate-bounce" priority />
        <p className="text-[15px] font-extrabold text-c-text">{loadingPhrases[phraseIdx]}</p>
        <p className="text-[13px] text-c-text-sub">{t('new.loadingNote')}</p>
      </main>
    )
  }

  // 로그인 확인 중
  if (isLoggedIn === null) {
    return (
      <main className="-mx-4 -mt-2 -mb-8 bg-c-bg px-4 pb-8 pt-4 shadow-[0_0_0_100vmax_var(--c-bg)] [clip-path:inset(0_-100vmax_-100vmax)] flex min-h-[60vh] items-center justify-center">
        <p className="text-sm text-c-text-sub">{t('new.checking')}</p>
      </main>
    )
  }

  // 비로그인
  if (!isLoggedIn) {
    return (
      <main className="-mx-4 -mt-2 -mb-8 bg-c-bg px-4 pb-8 pt-4 shadow-[0_0_0_100vmax_var(--c-bg)] [clip-path:inset(0_-100vmax_-100vmax)] flex flex-col gap-5">
        <h1 className="text-lg font-black text-c-text">{t('new.title')}</h1>
        <Card className="flex flex-col items-center gap-4 p-6 text-center">
          <Image src="/mascot.svg" alt="" width={56} height={56} />
          <p className="text-[15px] font-extrabold">{t('new.loginRequired')}</p>
          <p className="text-[13px] text-c-text-sub">{t('new.loginDesc')}</p>
          <a
            href={GOOGLE_LOGIN_URL}
            className={`${buttonClass('primary', 'md')} w-full`}
          >
            {t('new.loginWithGoogle')}
          </a>
        </Card>
      </main>
    )
  }

  // 로그인 상태 — 슬롯 선택 + 요청 주제
  return (
    <main className="-mx-4 -mt-2 -mb-8 bg-c-bg px-4 pb-8 pt-4 shadow-[0_0_0_100vmax_var(--c-bg)] [clip-path:inset(0_-100vmax_-100vmax)] flex flex-col gap-5">
      <div>
        <h1 className="text-[22px] font-black leading-tight text-c-text">{t('new.title')}</h1>
      </div>
      <p className="text-[13px] leading-relaxed text-c-text-sub">{t('new.guideline')}</p>

      {/* 요청 주제 입력 */}
      <div className="flex flex-col gap-1.5">
        <label className="text-[13px] font-extrabold" htmlFor="topics">
          {t('new.topicsLabel')}
        </label>
        <input
          id="topics"
          type="text"
          value={topics}
          onChange={(e) => setTopics(e.target.value)}
          placeholder={t('new.topicsPlaceholder')}
          className="w-full rounded-card border border-c-line bg-c-surface px-4 py-3 text-sm text-c-text"
          maxLength={100}
        />
        <p className="text-[12px] text-c-text-sub">{t('new.topicsHint')}</p>
      </div>

      {(error || jobError) && (
        <p className="rounded-card border border-c-line bg-c-surface-soft px-4 py-3 text-[13px] font-bold text-c-danger">
          {error || t('new.errorFallback')}
        </p>
      )}

      <PersonSlotPicker profiles={profiles} onComplete={handleComplete} />
    </main>
  )
}
