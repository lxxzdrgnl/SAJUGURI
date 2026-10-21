import { getTranslations } from 'next-intl/server'
import { Link } from '@/i18n/navigation'
import { buttonClass } from '@/components/ui/Button'
import ScreenShell from '@/components/ui/ScreenShell'

/** 로케일 내 404 — 새 디자인(단색 면 + 너구리). */
export default async function NotFound() {
  const t = await getTranslations('notFound')
  return (
    <ScreenShell center className="flex-col gap-5 text-center">
      <div className="flex h-24 w-24 items-center justify-center rounded-card bg-c-surface-soft">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/mascot.svg" alt="" width={64} height={64} />
      </div>
      <p className="font-display text-[64px] font-normal leading-none text-c-text">404</p>
      <div>
        <p className="text-lg font-extrabold text-c-text">{t('title')}</p>
        <p className="mt-1 text-sm text-c-text-sub">{t('desc')}</p>
      </div>
      <Link href="/" className={buttonClass('primary', 'md')}>
        {t('home')}
      </Link>
    </ScreenShell>
  )
}
