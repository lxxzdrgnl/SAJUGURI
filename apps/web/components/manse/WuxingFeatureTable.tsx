import { getTranslations } from 'next-intl/server'
import type { SajuCalcResponse } from '@sajuguri/api-client'
import { ohaengVar, ohaengTintVar } from '@/lib/ohaeng'
import Accordion from '@/components/ui/Accordion'

/** 오행 특성 참고표 (정적) — WuxingFeatureTable.vue 데이터 보존, 문구는 messages, 과다/부족 오행 강조 */
const FEATURES = [
  { el: '목', key: 'mok' },
  { el: '화', key: 'hwa' },
  { el: '토', key: 'to' },
  { el: '금', key: 'geum' },
  { el: '수', key: 'su' },
] as const

export default async function WuxingFeatureTable({ data }: { data: SajuCalcResponse }) {
  const t = await getTranslations('manse.charts.feature')
  const dominant = data.dominant_elements ?? []
  const weak = data.weak_elements ?? []

  return (
    <Accordion title={t('title')}>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[420px] border-collapse text-left text-[11px]">
          <thead>
            <tr className="border-b border-c-text">
              <th className="pb-2 pt-1 pr-2 text-[11px] font-extrabold text-c-text">{t('colEl')}</th>
              <th className="pb-2 pt-1 pr-2 text-[11px] font-extrabold text-c-text-sub">{t('colDir')}</th>
              <th className="pb-2 pt-1 pr-2 text-[11px] font-extrabold text-c-text-sub">{t('colTraits')}</th>
              <th className="pb-2 pt-1 pr-2 text-[11px] font-extrabold text-c-text-sub">{t('colBody')}</th>
              <th className="pb-2 pt-1 text-[11px] font-extrabold text-c-text-sub">{t('colJobs')}</th>
            </tr>
          </thead>
          <tbody>
            {FEATURES.map((f, idx) => {
              const isOver = dominant.includes(f.el)
              const isLack = weak.includes(f.el)
              const color = ohaengVar(f.el)
              const tint = ohaengTintVar(f.el)
              const isLast = idx === FEATURES.length - 1
              return (
                <tr
                  key={f.el}
                  className={`${isLast ? '' : 'border-b border-c-line'}`}
                  style={isOver || isLack ? { background: tint } : undefined}
                >
                  <td className="py-2.5 pr-2">
                    <span className="flex items-center gap-1 whitespace-nowrap">
                      <span
                        className="inline-flex h-6 w-6 items-center justify-center rounded-lg border border-c-line bg-c-surface text-sm font-black"
                        style={{ color }}
                      >
                        {f.el}
                      </span>
                      {isOver && (
                        <span className="rounded-pill bg-c-unlucky-bg px-1.5 py-px text-[9px] font-extrabold text-c-unlucky-fg">
                          {t('over')}
                        </span>
                      )}
                      {isLack && (
                        <span className="rounded-pill bg-c-lucky-bg px-1.5 py-px text-[9px] font-extrabold text-c-lucky-fg">
                          {t('lack')}
                        </span>
                      )}
                    </span>
                  </td>
                  <td className="py-2.5 pr-2 text-c-text-sub">{t(`row_${f.key}.dir`)}</td>
                  <td className="py-2.5 pr-2 font-bold text-c-text">{t(`row_${f.key}.traits`)}</td>
                  <td className="py-2.5 pr-2 text-c-text-sub">{t(`row_${f.key}.body`)}</td>
                  <td className="py-2.5 text-c-text-sub">{t(`row_${f.key}.jobs`)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </Accordion>
  )
}
