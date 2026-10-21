'use client'

/**
 * /question — 한줄 상담 페이지.
 * 흐름: 만세력 선택 모달(시트) → 질문 입력 → POST /api/question → 결과 카드.
 * - 진입 시 시트 자동 오픈 (미선택 상태)
 * - 선택 완료 후 질문 입력 textarea + 제출 노출
 * - 선택된 만세력 카드에서 "다시 선택" 버튼으로 시트 재오픈
 */
import { useEffect, useState } from 'react'
import { useTranslations, useLocale } from 'next-intl'
import type { ProfileResponse, QuestionRequest, ToolChartItem } from '@sajuguri/api-client'
import { askQuestion, shareConsultation } from '@sajuguri/api-client'
import { api } from '@/lib/api'
import MascotTinted from '@/components/ui/MascotTinted'
import MansePickerSheet, { type MansePick } from '@/components/manse/MansePickerSheet'
import Markdown from '@/components/ui/Markdown'
import { renderTextWithCharts } from '@/lib/chat/chartMarkers'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import ShareModal from '@/components/ui/ShareModal'
import { useShareModal } from '@/lib/hooks/useShareModal'

// ── 메인 페이지 ──────────────────────────────────────────────────────────────

export default function QuestionPage() {
  const t = useTranslations('question')
  const locale = useLocale()

  const [sheetOpen, setSheetOpen] = useState(false)
  const [selectedInput, setSelectedInput] = useState<MansePick | null>(null)
  const [selectedLabel, setSelectedLabel] = useState('')
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<{ id: number; headline: string; content: string; category: string; charts?: ToolChartItem[]; more?: ToolChartItem[] } | null>(null)
  const { shareUrl, sharing, share, close } = useShareModal()

  // 프로필 목록 — 클라이언트에서 로드 (SSR 없음, 게스트 허용 페이지)
  const [profiles, setProfiles] = useState<ProfileResponse[]>([])

  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then((r) => r.ok ? r.json() : null)
      .then((user) => {
        if (!user) return
        return fetch('/api/profiles', { credentials: 'include' })
          .then((r) => r.ok ? r.json() : [])
          .then(setProfiles)
      })
      .catch(() => {})
  }, [])

  // 진입 시 만세력 미선택이면 시트 자동 오픈
  useEffect(() => {
    if (!selectedInput) {
      setSheetOpen(true)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function handlePick(pick: MansePick) {
    setSelectedInput(pick)
    setSelectedLabel(pick.name)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!selectedInput) {
      setSheetOpen(true)
      return
    }
    const q = question.trim()
    if (q.length < 10) {
      setError(t('errorQuestionShort'))
      return
    }
    setLoading(true)
    setError('')
    try {
      const body: QuestionRequest = {
        birth_date: selectedInput.birth_date,
        birth_time: selectedInput.birth_time,
        gender: selectedInput.gender,
        calendar: selectedInput.calendar,
        is_leap_month: selectedInput.is_leap_month,
        ...(selectedInput.birth_longitude != null
          ? { birth_longitude: selectedInput.birth_longitude }
          : {}),
        name: selectedInput.name || undefined,
        question: q,
        language: locale,
      }
      const res = await askQuestion(api, body)
      setResult(res)
    } catch {
      setError(t('errorFallback'))
    } finally {
      setLoading(false)
    }
  }

  function handleShare() {
    if (!result || sharing) return
    share(() => shareConsultation(api, result.id).then(({ share_url }) => share_url))
  }

  // 결과 화면
  if (result) {
    // 채팅과 동일 — charts(tool→payload) 맵으로 content의 [[chart:...]] 마커를 인라인
    // ToolCard로 렌더한다. 가벼운 질문은 마커가 없어 텍스트만 나온다.
    const toolByName: Record<string, Record<string, unknown>> = Object.fromEntries(
      (result.charts ?? []).map((c) => [c.tool, c.payload as Record<string, unknown>]),
    )

    return (
      <main className="-mx-4 -mt-2 -mb-8 flex min-h-[calc(100vh-56px)] flex-col gap-5 px-4 pb-8 pt-2">
        <h1 className="font-display text-xl font-normal text-c-text">{t('title')}</h1>

        <Card tone="plain" className="p-5">
          <p className="mb-3 text-[11px] font-extrabold uppercase tracking-widest text-c-text-sub">
            {t('resultLabel')}
          </p>
          <p className="mb-2 text-[18px] font-black leading-snug text-c-text">{result.headline}</p>
          <div className="flex flex-col gap-3">
            {renderTextWithCharts(result.content, toolByName, 'q', {
              renderText: (seg, key) => (
                <Markdown key={key} className="text-[14px] text-c-text">{seg}</Markdown>
              ),
            })}
          </div>
          <span className="mt-4 inline-block rounded-pill bg-c-surface-soft px-3 py-0.5 text-[11px] font-extrabold text-c-text-sub">
            {result.category}
          </span>
        </Card>

        <div className="flex flex-col gap-2">
          <Button type="button" variant="primary" onClick={handleShare} disabled={sharing} className="w-full disabled:opacity-60">
            {sharing ? t('sharing') : t('share')}
          </Button>
          <Button
            type="button"
            variant="secondary"
            className="w-full"
            onClick={() => { setResult(null); setQuestion(''); close() }}
          >
            {t('askAgain')}
          </Button>
        </div>

        <ShareModal
          open={shareUrl !== null}
          url={shareUrl ?? ''}
          title={t('share')}
          onClose={close}
        />
      </main>
    )
  }

  return (
    <main className="-mx-4 -mt-2 -mb-8 flex min-h-[calc(100vh-56px)] flex-col gap-5 px-4 pb-8 pt-2">
      <div>
        <h1 className="font-display text-2xl font-normal leading-tight text-c-text">{t('title')}</h1>
      </div>
      <p className="text-[13px] text-c-text-sub">{t('desc')}</p>

      <MansePickerSheet
        open={sheetOpen}
        onClose={() => setSheetOpen(false)}
        profiles={profiles}
        title={t('pickSheet.title')}
        onPick={handlePick}
      />

      {/* 선택된 만세력 카드 */}
      <div className="flex flex-col gap-1.5">
        <p className="text-[13px] font-extrabold text-c-text">{t('birthLabel')}</p>
        {selectedInput ? (
          <Card tone="plain" className="flex items-center gap-3 p-4">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-full bg-c-surface-soft">
              <MascotTinted stem={selectedInput.day_stem ?? null} width={38} height={38} />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-[14px] font-extrabold text-c-text">{selectedLabel}</span>
              <span className="block text-xs text-c-text-sub">{selectedInput.birth_date}</span>
            </span>
            <Button type="button" variant="secondary" size="sm" className="shrink-0" onClick={() => setSheetOpen(true)}>
              {t('changeBirth')}
            </Button>
          </Card>
        ) : (
          <button
            type="button"
            className="flex w-full items-center gap-3 rounded-card bg-c-surface-soft p-4 text-left text-c-text transition-transform active:scale-[0.99]"
            onClick={() => setSheetOpen(true)}
          >
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-c-accent text-c-on-accent">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                <path d="M12 5 V19 M5 12 H19" />
              </svg>
            </span>
            <span className="text-[14px] font-extrabold">{t('selectBirth')}</span>
          </button>
        )}
      </div>

      {/* 질문 입력 — 만세력 선택 후에만 활성 */}
      {selectedInput && (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="question" className="text-[13px] font-extrabold text-c-text">
              {t('questionLabel', { name: selectedLabel })}
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={t('questionPlaceholder')}
              className="w-full resize-none rounded-card border border-c-line bg-c-surface px-4 py-3 text-sm leading-relaxed text-c-text placeholder:text-c-text-sub focus:outline-none focus:ring-2 focus:ring-c-accent"
              rows={3}
              minLength={10}
              maxLength={200}
            />
            <p className="text-right text-[11px] text-c-text-sub">{question.length}/200</p>
          </div>

          {error && (
            <p className="rounded-card border border-c-danger px-4 py-3 text-[13px] font-bold text-c-danger">
              {error}
            </p>
          )}

          <Button type="submit" variant="primary" disabled={loading} className="w-full disabled:opacity-60">
            {loading ? t('submitting') : t('submit')}
          </Button>
        </form>
      )}
    </main>
  )
}
