import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { serverApi } from '@/lib/api'
import { getSharedConsultation } from '@sajuguri/api-client'
import type { ConsultationDetail } from '@sajuguri/api-client'
import Markdown from '@/components/ui/Markdown'
import Card from '@/components/ui/Card'
import { buttonClass } from '@/components/ui/Button'
import { renderTextWithCharts } from '@/lib/chat/chartMarkers'

export const dynamic = 'force-dynamic'

async function fetchShared(token: string): Promise<ConsultationDetail | null> {
  try {
    return await getSharedConsultation(serverApi, token)
  } catch {
    return null
  }
}

// OG 메타 — 카카오/트위터 미리보기
export async function generateMetadata({
  params,
}: {
  params: Promise<{ token: string }>
}): Promise<Metadata> {
  const { token } = await params
  const t = await getTranslations('question.shared')
  const detail = await fetchShared(token)

  if (!detail) {
    return { title: t('notFoundTitle'), robots: { index: false } }
  }

  // 이름이 있으면 "{이름}님의 한줄상담", 없으면(게스트) "님의" 없는 익명 제목.
  const title = detail.name
    ? `${detail.name}님의 한줄상담 · ${detail.headline} | 사주구리`
    : `사주구리 한줄상담 · ${detail.headline}`
  return {
    title,
    description: detail.headline,
    robots: { index: false },
    openGraph: {
      title,
      description: detail.headline,
      siteName: '사주구리',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description: detail.headline,
    },
  }
}

export default async function SharedConsultationPage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params
  const t = await getTranslations('question.shared')
  const detail = await fetchShared(token)

  if (!detail) {
    return (
      <main className="-mx-4 -mt-2 -mb-8 min-h-[calc(100vh-56px)] bg-c-bg px-4 pb-8 pt-16 text-center">
        <p className="text-[15px] font-extrabold text-c-text">{t('notFoundTitle')}</p>
        <p className="mt-2 text-[13px] text-c-text-sub">{t('notFoundBody')}</p>
      </main>
    )
  }

  const tq = await getTranslations('question')

  return (
    <main className="-mx-4 -mt-2 -mb-8 flex min-h-[calc(100vh-56px)] flex-col gap-5 bg-c-bg px-4 pb-8 pt-2">
      <h1 className="font-display text-xl font-normal text-c-text">{tq('title')}</h1>

      {/* 질문 */}
      <Card tone="soft" className="p-4">
        <p className="mb-1 text-[11px] font-extrabold uppercase tracking-widest text-c-text-sub">
          {tq('questionHeader')}
        </p>
        <p className="text-[14px] font-bold text-c-text">{detail.question}</p>
      </Card>

      {/* 상담 결과 — 채팅과 동일: content의 [[chart:...]] 마커를 인라인 ToolCard로 렌더 */}
      <Card tone="plain" className="p-5">
        <p className="mb-3 text-[11px] font-extrabold uppercase tracking-widest text-c-text-sub">
          {tq('resultLabel')}
        </p>
        <p className="mb-2 text-[18px] font-black leading-snug text-c-text">{detail.headline}</p>
        <div className="flex flex-col gap-3">
          {renderTextWithCharts(
            detail.content,
            Object.fromEntries((detail.charts ?? []).map((c) => [c.tool, c.payload])) as Record<string, Record<string, unknown>>,
            'sq',
            { renderText: (seg, key) => <Markdown key={key} className="text-[14px] text-c-text">{seg}</Markdown> },
          )}
        </div>
        <span className="mt-4 inline-block rounded-pill bg-c-surface-soft px-3 py-0.5 text-[11px] font-extrabold text-c-text-sub">
          {detail.category}
        </span>
      </Card>

      {/* 나도 한줄상담 받기 CTA */}
      <Card tone="counsel" className="mt-2 p-4">
        <p className="mb-1 text-[14px] font-extrabold text-c-text">{t('ctaTitle')}</p>
        <p className="mb-3 text-[13px] text-c-text-sub">{t('ctaBody')}</p>
        <a
          href="/question"
          className={`${buttonClass('primary', 'md')} w-full`}
        >
          {t('ctaButton')}
        </a>
      </Card>
    </main>
  )
}
