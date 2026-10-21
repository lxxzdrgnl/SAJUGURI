'use client'

import type { ProfileResponse } from '@sajuguri/api-client'
import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/navigation'
import Card from '@/components/ui/Card'
import { buttonClass } from '@/components/ui/Button'
import { trackProductView } from '@/lib/products/track'

/** 구리구리 상담 진입 카드. hero=캐러셀 큰 카드, row=목록 행. */
export default function CounselCard({
  size,
  profile = null,
}: {
  size: 'hero' | 'row'
  profile?: ProfileResponse | null
}) {
  const t = useTranslations('home.counsel')
  const onClick = () => trackProductView('guriguri_counsel', profile)

  if (size === 'row') {
    return (
      <Link href="/chat" onClick={onClick} className="block">
        <Card tone="counsel" className="flex items-center gap-3 p-4">
          <img src="/mascot/thumbsup.png" alt="" width={48} height={48} className="h-12 w-12 shrink-0 object-contain" />
          <div className="min-w-0 flex-1">
            <p className="font-display text-sm font-normal">{t('title')}</p>
            <p className="mt-0.5 text-xs opacity-80">{t('desc')}</p>
          </div>
        </Card>
      </Link>
    )
  }

  return (
    <Card tone="counsel" className="flex h-full flex-col justify-between gap-4 p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-display text-xl font-normal leading-snug">{t('title')}</p>
          <p className="mt-2 text-sm opacity-80">{t('desc')}</p>
        </div>
        <img src="/mascot/thumbsup.png" alt="" width={96} height={96} className="h-24 w-24 shrink-0 object-contain" />
      </div>
      <Link href="/chat" onClick={onClick} className={`${buttonClass('primary', 'md')} self-start`}>
        {t('cta')}
      </Link>
    </Card>
  )
}
