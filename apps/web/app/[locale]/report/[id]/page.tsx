import { getTranslations } from 'next-intl/server'
import { serverAuthApi } from '@/lib/serverAuth'
import { getReport } from '@sajuguri/api-client'
import ReportView from '@/components/report/ReportView'
import MascotTinted from '@/components/ui/MascotTinted'
import Card from '@/components/ui/Card'

export default async function ReportDetailPage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>
}) {
  const { id } = await params
  const t = await getTranslations('report')
  const tf = await getTranslations('manse.form')

  let report = null
  try {
    const api = await serverAuthApi()
    report = await getReport(api, Number(id))
  } catch {
    report = null
  }

  if (!report) {
    return (
      <main className="-mx-4 -mt-2 -mb-8 min-h-[calc(100dvh-3.5rem)] px-4 pt-16 text-center">
        <p className="text-[15px] font-extrabold text-c-text-sub">{t('errorFallback')}</p>
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
      {/* 원국 한 줄 요약 — 마스코트 아바타 포함 */}
      <Card tone="soft" className="flex items-center gap-3 p-3">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded-full bg-c-surface">
          <MascotTinted width={40} height={40} />
        </span>
        <span className="text-[14px] font-bold text-c-text">{summaryLine}</span>
      </Card>

      <ReportView report={report} reportId={Number(id)} />

      {/* 안내 — 콘텐츠 하단으로 이동 */}
      <p className="pb-2 text-center text-[13px] text-c-text-sub">{t('page.guideText')}</p>
    </main>
  )
}
