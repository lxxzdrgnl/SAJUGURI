'use client'

import { useEffect, useState } from 'react'
import { useTranslations } from 'next-intl'
import { api } from '@/lib/api'
import type { IlJinEntry } from '@sajuguri/api-client'
import { calendarGrid, dateKey, prevMonth, nextMonth } from '@/lib/manse/ilJin'

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']
const MONTH_NAMES = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']

/** 일진 달력 — 월 달력 + 간지·음력·절기 (IlJinCalendar.vue 이식). 그리드 로직은 lib/manse/ilJin */
export default function IlJinCalendar() {
  const t = useTranslations('manse.charts.ilJin')
  const now = new Date()
  const todayStr = dateKey(now.getFullYear(), now.getMonth() + 1, now.getDate())

  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [entries, setEntries] = useState<IlJinEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    let alive = true
    setLoading(true)
    setError(false)
    const q = new URLSearchParams({ year: String(year), month: String(month) })
    api.get<IlJinEntry[]>(`/api/saju/il-jin?${q}`)
      .then((d) => { if (alive) { setEntries(d); setLoading(false) } })
      .catch(() => { if (alive) { setError(true); setLoading(false) } })
    return () => { alive = false }
  }, [year, month])

  const grid = calendarGrid(year, month, entries)
  const go = (fn: typeof prevMonth) => { const n = fn(year, month); setYear(n.year); setMonth(n.month) }

  return (
    <section className="rounded-card border border-c-line bg-c-surface p-5 text-c-text">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-[15px] font-extrabold">{t('title')}</h3>
        <div className="flex items-center gap-2">
          <button type="button" onClick={() => go(prevMonth)} className="flex h-8 w-8 items-center justify-center rounded-pill border border-c-line bg-c-surface text-sm font-black">‹</button>
          <span className="min-w-[88px] text-center text-sm font-extrabold">{year} {MONTH_NAMES[month - 1]}</span>
          <button type="button" onClick={() => go(nextMonth)} className="flex h-8 w-8 items-center justify-center rounded-pill border border-c-line bg-c-surface text-sm font-black">›</button>
        </div>
      </div>

      {error ? (
        <p className="py-6 text-center text-sm text-c-text-sub">{t('error')}</p>
      ) : loading ? (
        <p className="py-6 text-center text-sm text-c-text-sub">{t('loading')}</p>
      ) : (
        <>
          <div className="grid grid-cols-7 gap-1">
            {WEEKDAYS.map((wd, i) => (
              <div key={wd} className={`py-1 text-center text-[12px] font-bold ${i === 0 ? 'text-c-danger' : i === 6 ? 'text-c-oh-su' : 'text-c-text-sub'}`}>{wd}</div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1">
            {grid.map((cell, idx) => {
              const isToday = cell.date === todayStr
              return (
                <div
                  key={idx}
                  className={`min-h-[72px] rounded-lg p-1 ${isToday ? 'border-[1.5px] border-c-text bg-c-surface-soft' : cell.entry?.solar_term ? 'bg-c-oh-to-tint' : ''}`}
                >
                  {cell.day && (
                    <>
                      <div className={`text-[13px] font-bold ${isToday ? 'text-c-text' : idx % 7 === 0 ? 'text-c-danger' : idx % 7 === 6 ? 'text-c-oh-su' : 'text-c-text'}`}>{cell.day}</div>
                      {cell.entry?.solar_term && <div className="text-[11px] font-semibold text-c-oh-to">{cell.entry.solar_term}</div>}
                      {cell.entry && <div className="text-[12px] font-semibold text-c-text-sub">{cell.entry.ganji_name}</div>}
                      {cell.entry && (
                        <div className={`text-[11px] ${cell.entry.is_leap_month ? 'text-c-oh-su' : 'text-c-text-sub'}`}>
                          {cell.entry.is_leap_month ? t('leapMark') : ''}{cell.entry.lunar_month}/{cell.entry.lunar_day}
                        </div>
                      )}
                    </>
                  )}
                </div>
              )
            })}
          </div>
          <div className="mt-2 flex flex-wrap gap-3 border-t border-c-line pt-3 text-[11px] text-c-text-sub">
            <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded border-[1.5px] border-c-text bg-c-surface-soft" />{t('today')}</span>
            <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded bg-c-oh-to-tint" />{t('solarTerm')}</span>
            <span className="flex items-center gap-1"><span className="text-c-oh-su">{t('leapMark')}</span>{t('leap')}</span>
          </div>
        </>
      )}
    </section>
  )
}
