'use client'

import { useTranslations } from 'next-intl'
import type { ProfileResponse } from '@sajuguri/api-client'
import { Link } from '@/i18n/navigation'
import { buttonClass } from '@/components/ui/Button'
import { STEM_HANJA } from '@sajuguri/core'
import { manseNavQuery, profileToManseSource } from '@/lib/manse/query'

/** 헤더의 대표 일간 칩 — 있으면 내 만세력 결과로, 없으면 일간 찾기(만세력 입력)로. */
export default function IlganChip({ profile }: { profile: ProfileResponse | null }) {
  const t = useTranslations('nav')
  const stem = profile?.day_stem
  if (!profile || !stem) {
    return (
      <Link href="/manse/new" className={`${buttonClass('secondary', 'sm')} shrink-0 whitespace-nowrap`}>
        {t('findIlgan')}
      </Link>
    )
  }
  const q = manseNavQuery(profileToManseSource(profile))
  return (
    <Link
      href={q ? `/manse/result?${q}` : '/manse'}
      className={`${buttonClass('secondary', 'sm')} min-w-0 max-w-[60%]`}
    >
      <span className="truncate">
        {t('ilganChip', { hanja: STEM_HANJA[stem] ?? '', name: profile.name, stem })}
      </span>
    </Link>
  )
}
