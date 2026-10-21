import { getTranslations } from 'next-intl/server'
import { sinSalLabel } from '@/lib/manse/termLabel'
import type { SajuCalcResponse } from '@sajuguri/api-client'
import { ohaengVar } from '@/lib/ohaeng'
import { pillarSlots, sinSalsForPillar, jiJangGanText } from '@/lib/manse/pillars'
import Accordion from '@/components/ui/Accordion'

/** 12운성·신살·지장간 상세 — 기둥별 (Table.vue 하단부 이식). 길신=초록·흉살=주황 부호 */
export default async function DetailAccordion({ data }: { data: SajuCalcResponse }) {
  const t = await getTranslations('manse.charts.detail')
  const tt = await getTranslations('manse.terms')
  const slots = pillarSlots(data)

  return (
    <Accordion title={t('title')}>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[320px] table-fixed border-collapse text-center">
          <thead>
            <tr className="border-b border-c-text">
              {/* 행 라벨 열 */}
              <th className="w-14 py-2" />
              {slots.map((s) => (
                <th
                  key={s.loc}
                  className={`pb-2 pt-2 text-[11px] font-extrabold ${
                    s.loc === 'day' ? 'text-c-text' : 'text-c-text-sub'
                  }`}
                >
                  {s.colLabel}
                  {s.loc === 'day' ? ' ★' : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="align-top">
            {/* 12운성 행 */}
            <tr className="border-b border-c-line">
              <td className="py-2.5 pr-1 text-[11px] font-extrabold text-c-text-sub">{t('twelveWun')}</td>
              {slots.map((s) => (
                <td key={s.loc} className="py-2.5 text-sm font-extrabold" style={{ color: s.pillar ? ohaengVar(s.pillar.branch_element) : undefined }}>
                  {s.pillar ? s.pillar.twelve_wun : t('none')}
                </td>
              ))}
            </tr>
            {/* 지장간 행 */}
            <tr className="border-b border-c-line">
              <td className="py-2.5 pr-1 text-[11px] font-extrabold text-c-text-sub">{t('jiJangGan')}</td>
              {slots.map((s) => (
                <td key={s.loc} className="py-2.5 text-xs font-bold tracking-wide text-c-text">
                  {s.pillar ? jiJangGanText(data.ji_jang_gan, s.loc) || t('none') : t('none')}
                </td>
              ))}
            </tr>
            {/* 신살 행 */}
            <tr>
              <td className="py-2.5 pr-1 text-[11px] font-extrabold text-c-text-sub">{t('sinSal')}</td>
              {slots.map((s) => {
                const sals = s.pillar ? sinSalsForPillar(data.sin_sals, s.loc) : []
                return (
                  <td key={s.loc} className="py-2.5 text-[11px]">
                    {sals.length ? (
                      <div className="flex flex-col items-center gap-1">
                        {sals.map((sal) => {
                          const isLucky = sal.type === 'lucky'
                          const isUnlucky = sal.type === 'unlucky' || sal.type === 'warning'
                          return (
                            <span
                              key={sal.name}
                              className={`inline-block rounded-pill border px-1.5 py-px text-[10px] font-extrabold ${
                                isLucky
                                  ? 'border-transparent bg-c-lucky-bg text-c-lucky-fg'
                                  : isUnlucky
                                    ? 'border-transparent bg-c-unlucky-bg text-c-unlucky-fg'
                                    : 'border-c-line bg-c-surface text-c-text-sub'
                              }`}
                            >
                              {isLucky ? '+' : isUnlucky ? '-' : '·'}{sinSalLabel(tt, sal.name)}
                            </span>
                          )
                        })}
                      </div>
                    ) : (
                      <span className="text-c-text-sub">{t('none')}</span>
                    )}
                  </td>
                )
              })}
            </tr>
          </tbody>
        </table>
      </div>
    </Accordion>
  )
}
