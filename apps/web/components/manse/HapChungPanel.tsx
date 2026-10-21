'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import type { SajuCalcResponse, Pillar } from '@sajuguri/api-client'
import { ohaengVar, ohaengTintVar } from '@/lib/ohaeng'
import { ALL_TABS, buildEntries, hasData, activePillars, type Entry, type TabKey, type PillarKey } from '@/lib/manse/hapChung'

const PILLAR_KEY = { year: 'pillarYear', month: 'pillarMonth', day: 'pillarDay', hour: 'pillarHour' } as const
const SHORT_KEY = { year: 'shortYear', month: 'shortMonth', day: 'shortDay', hour: 'shortHour' } as const
const EL_KEY: Record<string, string> = { 목: 'elMok', 화: 'elHwa', 토: 'elTo', 금: 'elGeum', 수: 'elSu' }

const PALACE_WEIGHTS: Record<PillarKey, { stem: string; branch: string }> = {
  hour: { stem: '×1.0', branch: '×0.8' },
  day: { stem: '×1.5', branch: '×1.0' },
  month: { stem: '×1.0', branch: '×2.0' },
  year: { stem: '×1.0', branch: '×1.0' },
}

function pillarOf(data: SajuCalcResponse, p: PillarKey): Pillar | null {
  return (data[`${p}_pillar`] as Pillar | null) ?? null
}

/** 합충 분석 — 삼합/육합/충/형/파/해/원진 + 궁성 탭 (HapChungPanel.vue 이식). 엔트리 빌드는 lib/manse/hapChung */
export default function HapChungPanel({ data }: { data: SajuCalcResponse }) {
  const t = useTranslations('manse.charts.hapChung')
  const [tab, setTab] = useState<TabKey>('gung_seong')
  const active = activePillars(data)
  const entries = buildEntries(data, tab)
  const showWeight = tab === 'gung_seong'

  function sentence(e: Entry) {
    const desc = e.descPillars.length ? `(${e.descPillars.map((p) => t(SHORT_KEY[p])).join('-')}) ` : ''
    const [a = '', b = ''] = e.chars
    return t.rich(`rel.${e.kind}`, {
      b: (c) => <b className="font-black text-c-chart-accent">{c}</b>,
      desc,
      name: a,
      a,
      b2: b,
      pillar: e.pillar ? t(SHORT_KEY[e.pillar]) : '',
      branch: a,
      vacant: (e.vacant ?? []).join(', '),
    })
  }

  function Box({ ch, on, weight }: { ch?: string; on: boolean; weight?: string }) {
    return (
      <div
        className={`flex h-14 w-full flex-col items-center justify-center rounded-xl border ${
          on ? 'border-c-text bg-c-text' : 'border-c-line bg-c-surface'
        }`}
      >
        <span className={`font-serif text-xl font-black leading-none ${on ? 'text-c-bg' : 'text-c-text'}`}>
          {ch ?? '—'}
        </span>
        {/* 가중치 영역 고정 — 없으면 빈 문자열로 유지해 높이 보장 */}
        <span className={`mt-0.5 h-[14px] text-[9px] font-bold leading-none ${on ? 'text-c-bg opacity-70' : 'text-c-text-sub'}`}>
          {weight ?? ''}
        </span>
      </div>
    )
  }

  function MiniGrid({ stems, branches }: { stems: PillarKey[]; branches: PillarKey[] }) {
    return (
      <div className="mt-2 grid gap-1.5" style={{ gridTemplateColumns: `repeat(${active.length}, 1fr)` }}>
        {active.map((pk) => {
          const p = pillarOf(data, pk)
          return (
            <div key={pk} className="flex min-w-0 flex-col items-center gap-1">
              <span className="text-[10px] text-c-text-sub">{t(PILLAR_KEY[pk])}</span>
              <Box ch={p?.stem} on={stems.includes(pk)} weight={showWeight ? PALACE_WEIGHTS[pk].stem : undefined} />
              <Box ch={p?.branch} on={branches.includes(pk)} weight={showWeight ? PALACE_WEIGHTS[pk].branch : undefined} />
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <section className="overflow-hidden rounded-card border border-c-line bg-c-surface text-c-text">
      <h3 className="px-5 pt-5 text-[15px] font-extrabold">{t('title')}</h3>

      <div className="flex flex-wrap gap-1.5 px-5 py-3">
        {ALL_TABS.map((tabKey) => {
          const has = hasData(data, tabKey)
          const isActive = tab === tabKey
          return (
            <button
              key={tabKey}
              type="button"
              onClick={() => setTab(tabKey)}
              className={`rounded-pill border px-2.5 py-1 text-[11px] font-extrabold ${
                isActive
                  ? 'border-transparent bg-c-accent text-c-on-accent'
                  : has
                    ? 'border-c-text bg-c-surface text-c-text'
                    : 'border-c-line bg-c-surface text-c-text-sub'
              }`}
            >
              {t(`tab.${tabKey}`)}
            </button>
          )
        })}
      </div>

      <div className="border-t border-c-line px-5 py-4">
        {showWeight ? (
          <>
            <p className="mb-2 text-xs leading-relaxed text-c-text-sub">{t('gungSeongDesc')}</p>
            <MiniGrid stems={[]} branches={[]} />
          </>
        ) : entries.length === 0 ? (
          <p className="py-2 text-sm text-c-text-sub">{t('empty')}</p>
        ) : (
          <div className="flex flex-col gap-5">
            {entries.map((e, i) => (
              <div key={i} className="flex flex-col gap-1.5">
                <p className="text-sm leading-snug text-c-text">{sentence(e)}</p>
                {e.broken && <span className="w-fit rounded-pill bg-c-unlucky-bg px-2.5 py-0.5 text-[11px] font-extrabold text-c-unlucky-fg">{t('broken')}</span>}
                {e.resultEl && !e.broken && (
                  <span className="w-fit rounded-pill px-2.5 py-0.5 text-[11px] font-extrabold" style={{ color: ohaengVar(e.resultEl), background: ohaengTintVar(e.resultEl) }}>
                    {t('transform', { el: EL_KEY[e.resultEl] ? t(EL_KEY[e.resultEl]) : e.resultEl })}
                  </span>
                )}
                <MiniGrid stems={e.stems} branches={e.branches} />
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
