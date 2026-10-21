import { useTranslations } from 'next-intl'
import { ohaengVar } from '@/lib/ohaeng'
import { termLabel } from '@/lib/manse/termLabel'

/** 운(대운/연운/월운) 한 칸 — 상단 라벨·천간 타일·지지 타일·하단 십성·강조 배지 (DaeUnSlider·YeonUnSlider 공통 구조) */
export default function GanjiColumn({
  topLabel,
  stem,
  stemElement,
  branch,
  branchElement,
  stemTenGod,
  branchTenGod,
  twelveWun,
  highlight = false,
  badge,
  dim = false,
}: {
  topLabel: string
  stem: string
  stemElement: string
  branch: string
  branchElement: string
  stemTenGod?: string
  branchTenGod?: string
  twelveWun?: string
  highlight?: boolean
  badge?: string
  dim?: boolean
}) {
  const tt = useTranslations('manse.terms')
  // 평소=오행색 면 + 배경색 글자(두 모드 모두 대비 확보), 강조=표면 + 오행색 글자 + 본문색 라인
  const Tile = ({ ch, element }: { ch: string; element: string }) => (
    <div
      className={`flex h-11 w-11 items-center justify-center rounded-xl ${
        highlight ? 'border-[1.5px] border-c-text bg-c-surface' : ''
      }`}
      style={highlight ? undefined : { background: ohaengVar(element) }}
    >
      <span className="font-serif text-xl font-black leading-none" style={{ color: highlight ? ohaengVar(element) : 'var(--c-bg)' }}>
        {ch}
      </span>
    </div>
  )

  return (
    <div className={`flex shrink-0 flex-col items-center gap-1 ${dim ? 'opacity-50' : ''}`}>
      <span className="text-[11px] font-bold text-c-text-sub">{topLabel}</span>
      {stemTenGod && <span className="text-[10px] text-c-text-sub">{termLabel(tt, stemTenGod)}</span>}
      <Tile ch={stem} element={stemElement} />
      <Tile ch={branch} element={branchElement} />
      {branchTenGod && <span className="text-[10px] text-c-text-sub">{termLabel(tt, branchTenGod)}</span>}
      {/* 12운성은 오행이 아니라 생애 단계 라벨 — 보조 텍스트색 */}
      {twelveWun && <span className="text-[10px] font-semibold text-c-text-sub">{twelveWun}</span>}
      {badge && <span className="mt-0.5 rounded-pill bg-c-accent px-2 py-0.5 text-[10px] font-extrabold text-c-on-accent">{badge}</span>}
    </div>
  )
}
