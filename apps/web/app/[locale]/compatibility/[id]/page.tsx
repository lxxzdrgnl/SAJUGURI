import { getTranslations } from 'next-intl/server'
import { serverAuthApi } from '@/lib/serverAuth'
import { getCompatibilityReport } from '@sajuguri/api-client'
import Card from '@/components/ui/Card'
import CompatibilityView from '@/components/compatibility/CompatibilityView'
import ScreenShell from '@/components/ui/ScreenShell'

export default async function CompatibilityDetailPage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>
}) {
  const { id } = await params
  const t = await getTranslations('compatibility')

  let detail = null
  try {
    const api = await serverAuthApi()
    detail = await getCompatibilityReport(api, Number(id))
  } catch {
    detail = null
  }

  if (!detail) {
    return (
      <ScreenShell className="pt-2 text-center">
        <p className="text-[15px] font-extrabold text-c-text-sub">{t('view.errorFallback')}</p>
      </ScreenShell>
    )
  }

  const nameA = detail.person_a.name ?? t('scoreOverview.personA')
  const nameB = detail.person_b.name ?? t('scoreOverview.personB')

  return (
    <ScreenShell className="pt-2 flex flex-col gap-4">
      {/* 두 사람 요약 헤더 */}
      <Card className="flex items-center gap-2 px-4 py-3">
        <div className="flex flex-1 flex-col min-w-0">
          <span className="truncate text-[14px] font-extrabold text-c-text">{nameA}</span>
          {detail.person_a.birth_date && (
            <span className="text-[12px] text-c-text-sub">{detail.person_a.birth_date}</span>
          )}
        </div>
        <span className="shrink-0 text-[20px] text-c-text-sub font-black">♥</span>
        <div className="flex flex-1 flex-col items-end min-w-0">
          <span className="truncate text-[14px] font-extrabold text-c-text">{nameB}</span>
          {detail.person_b.birth_date && (
            <span className="text-[12px] text-c-text-sub">{detail.person_b.birth_date}</span>
          )}
        </div>
      </Card>

      <CompatibilityView detail={detail} />

      {/* 안내 — 콘텐츠 하단 */}
      <p className="pb-2 text-center text-[13px] text-c-text-sub">{t('view.guideText')}</p>
    </ScreenShell>
  )
}
