'use client'

import { useState, useEffect } from 'react'
import { useTranslations, useLocale } from 'next-intl'
import { useRouter, useSearchParams } from 'next/navigation'
import Image from 'next/image'
import { api } from '@/lib/api'
import { createReportJob } from '@sajuguri/api-client'
import { useGenerationJob } from '@/lib/hooks/useGenerationJob'
import type { SajuCalcRequest } from '@sajuguri/api-client'
import PageHeading from '@/components/ui/PageHeading'
import Card from '@/components/ui/Card'
import Button, { buttonClass } from '@/components/ui/Button'
import GoogleLoginLink from '@/components/auth/GoogleLoginLink'
import ScreenShell from '@/components/ui/ScreenShell'

const LOADING_PHRASE_COUNT = 6

export default function ReportNewPage() {
  const t = useTranslations('report')
  const locale = useLocale()
  const router = useRouter()
  const searchParams = useSearchParams()

  const { loading, error: jobError, start } = useGenerationJob((_type, resultId) => {
    router.replace(`/report/${resultId}`)
  })

  const [topics, setTopics] = useState('')
  const [error, setError] = useState('')
  const [phraseIdx, setPhraseIdx] = useState(0)
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null)

  // 로그인 상태 확인
  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then(r => setIsLoggedIn(r.ok))
      .catch(() => setIsLoggedIn(false))
  }, [])

  // 로딩 문구 순환
  useEffect(() => {
    if (!loading) return
    const timer = setInterval(() => {
      setPhraseIdx(i => (i + 1) % LOADING_PHRASE_COUNT)
    }, 3000)
    return () => clearInterval(timer)
  }, [loading])

  // 폴링 실패 시 에러 표시
  useEffect(() => {
    if (jobError) setError(t('errorFallback'))
  }, [jobError, t])

  // searchParams에서 birth 정보 추출
  function buildBirthInput(): SajuCalcRequest | null {
    const birth_date = searchParams.get('birth_date')
    const gender = searchParams.get('gender')
    if (!birth_date || !gender) return null
    return {
      name: searchParams.get('name') ?? undefined,
      birth_date,
      birth_time: searchParams.get('birth_time') ?? null,
      gender: (gender === 'female' ? 'female' : 'male') as 'male' | 'female',
      calendar: (searchParams.get('calendar') ?? 'solar') as 'solar' | 'lunar',
      is_leap_month: searchParams.get('is_leap_month') === 'true',
      ...(searchParams.get('birth_longitude') ? { birth_longitude: Number(searchParams.get('birth_longitude')) } : {}),
      ...(searchParams.get('birth_utc_offset') ? { birth_utc_offset: Number(searchParams.get('birth_utc_offset')) } : {}),
      ...(searchParams.get('city') ? { city: searchParams.get('city')! } : {}),
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const birthInput = buildBirthInput()
    if (!birthInput) {
      setError(t('errorMissingBirth'))
      return
    }
    setError('')
    try {
      const profileId = searchParams.get('profile_id')
      const { job_id } = await createReportJob(api, {
        birth_input: birthInput,
        ...(topics.trim() ? { request_topics: topics.trim() } : {}),
        ...(profileId ? { profile_id: Number(profileId) } : {}),
        language: locale,
      })
      start(job_id)
    } catch (err: unknown) {
      const status = (err as { status?: number })?.status
      if (status === 401) setError(t('errorLogin'))
      else if (status === 429) setError(t('errorLimit'))
      else setError(t('errorFallback'))
    }
  }

  // 로딩 중 화면
  if (loading) {
    return (
      <ScreenShell center className="flex-col gap-6 text-center">
        <Image src="/mascot.svg" alt="" width={72} height={72} className="animate-bounce" priority />
        <p className="text-[15px] font-extrabold text-c-text">{t(`loadingPhrase${phraseIdx}`)}</p>
        <p className="text-[13px] text-c-text-sub">{t('loadingNote')}</p>
      </ScreenShell>
    )
  }

  // 로그인 확인 중
  if (isLoggedIn === null) {
    return (
      <ScreenShell center>
        <p className="text-sm text-c-text-sub">{t('checking')}</p>
      </ScreenShell>
    )
  }

  // 비로그인
  if (!isLoggedIn) {
    return (
      <ScreenShell className="flex flex-col gap-5 pt-2">
        <h1 className="text-lg font-black text-c-text">{t('title')}</h1>
        <Card className="flex flex-col items-center gap-4 p-6 text-center">
          <Image src="/mascot.svg" alt="" width={56} height={56} />
          <p className="text-[15px] font-extrabold text-c-text">{t('loginRequired')}</p>
          <p className="text-[13px] text-c-text-sub">{t('loginDesc')}</p>
          <GoogleLoginLink
            
            className={`${buttonClass('primary', 'md')} w-full`}
          >
            {t('loginWithGoogle')}
          </GoogleLoginLink>
        </Card>
      </ScreenShell>
    )
  }

  // 로그인 상태 — 생성 폼
  return (
    <ScreenShell className="flex flex-col gap-5 pt-2">
      <PageHeading title={t('title')} accent="orange" />

      <p className="text-[13px] leading-relaxed text-c-text-sub">{t('guideline')}</p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-[13px] font-extrabold text-c-text" htmlFor="topics">
            {t('topicsLabel')}
          </label>
          <input
            id="topics"
            type="text"
            value={topics}
            onChange={e => setTopics(e.target.value)}
            placeholder={t('topicsPlaceholder')}
            className="h-12 w-full rounded-card border border-c-line bg-c-surface px-4 text-sm text-c-text placeholder:text-c-text-sub"
            maxLength={100}
          />
          <p className="text-[12px] text-c-text-sub">{t('topicsHint')}</p>
        </div>

        {error && (
          <p role="alert" className="rounded-card bg-c-surface-soft px-4 py-3 text-[13px] font-bold text-c-danger">
            {error}
          </p>
        )}

        <Button type="submit" className="w-full">
          {t('submit')}
        </Button>
      </form>
    </ScreenShell>
  )
}
