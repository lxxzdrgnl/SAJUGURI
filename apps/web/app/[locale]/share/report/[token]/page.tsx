import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { serverApi } from '@/lib/api'
import { getSharedReport } from '@sajuguri/api-client'
import ReportView from '@/components/report/ReportView'
import Card from '@/components/ui/Card'
import { buttonClass } from '@/components/ui/Button'

export const dynamic = 'force-dynamic'

// OG 메타 — 카카오 미리보기 (spec §7.5 핵심 요구)
export async function generateMetadata({
  params,
}: {
  params: Promise<{ token: string }>
}): Promise<Metadata> {
  const { token } = await params
  const t = await getTranslations('report.shared')
  const site = (await getTranslations('meta'))('siteName')
  let profileName = ''
  try {
    const report = await getSharedReport(serverApi, token)
    profileName = report.profile_name || ''
  } catch {
    /* fallback */
  }
  // 이름이 있으면 "{이름}님의 사주 리포트", 없으면(게스트) "님의" 없는 익명 제목.
  const hasName = Boolean(profileName)
  const title = hasName ? t('metaTitle', { name: profileName, site }) : t('metaTitleAnon', { site })
  const description = hasName ? t('metaDescription', { name: profileName }) : t('metaDescriptionAnon', { site })
  return {
    title,
    description,
    robots: { index: false },
    openGraph: {
      title,
      description,
      siteName: site,
    },
  }
}

export default async function SharedReportPage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params
  const t = await getTranslations('report.shared')
  const tr = await getTranslations('report')
  const tf = await getTranslations('manse.form')

  let report = null
  try {
    report = await getSharedReport(serverApi, token)
  } catch {
    report = null
  }

  if (!report) {
    return (
      <main className="-mx-4 -mt-2 -mb-8 min-h-[calc(100dvh-3.5rem)] px-4 pt-16 text-center">
        <p className="text-[15px] font-extrabold text-c-text-sub">{t('notFoundTitle')}</p>
        <p className="mt-2 text-[13px] text-c-text-sub">{t('notFoundDesc')}</p>
      </main>
    )
  }

  const bi = report.birth_input
  const summaryLine = [
    bi.name,
    bi.birth_date,
    bi.gender === 'male' ? tf('male') : tf('female'),
  ]
    .filter(Boolean)
    .join(' · ')

  return (
    <main className="-mx-4 -mt-2 -mb-8 flex min-h-[calc(100dvh-3.5rem)] flex-col gap-4 px-4 pb-8 pt-4">
      <Card tone="soft" className="p-3 text-[14px] font-bold">
        {summaryLine}
      </Card>

      {/* 공유 모드 — CTA 없음 */}
      <ReportView report={report} reportId={0} shareMode />

      {/* 안내 — 하단 */}
      <p className="pb-2 text-center text-[13px] text-c-text-sub">{tr('page.guideText')}</p>

      {/* 나도 확인 CTA */}
      <Card className="mt-2 p-5">
        <p className="mb-1 text-[14px] font-extrabold">{t('ctaTitle')}</p>
        <p className="mb-3 text-[13px] text-c-text-sub">{t('ctaDesc')}</p>
        <a
          href="/"
          className={`${buttonClass('primary', 'md')} w-full`}
        >
          {t('ctaBtn')}
        </a>
      </Card>
    </main>
  )
}
