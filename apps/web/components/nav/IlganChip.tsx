'use client'

import { useTranslations } from 'next-intl'
import type { ProfileResponse } from '@sajuguri/api-client'
import { Link } from '@/i18n/navigation'
import { buttonClass } from '@/components/ui/Button'
import { manseNavQuery, profileToManseSource } from '@/lib/manse/query'

/** 천간 한글 → 한자 */
const STEM_HANJA: Record<string, string> = {
  갑: '甲', 을: '乙', 병: '丙', 정: '丁', 무: '戊',
  기: '己', 경: '庚', 신: '辛', 임: '壬', 계: '癸',
}

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
