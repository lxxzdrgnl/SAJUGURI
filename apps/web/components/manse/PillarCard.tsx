import type { Pillar } from '@sajuguri/api-client'
import { ohaengVar, ohaengTintVar } from '@/lib/ohaeng'

/** 기둥 카드 1장 — kind: 'stem'(천간) | 'branch'(지지). 일주 기둥은 본문색 라인으로 강조 */
export default function PillarCard({
  pillar, kind, label, isDay = false,
}: {
  pillar: Pillar
  kind: 'stem' | 'branch'
  label?: string
  isDay?: boolean
}) {
  const hanja = kind === 'stem' ? pillar.stem_hanja : pillar.branch_hanja
  const kor = kind === 'stem' ? pillar.stem : pillar.branch
  const element = kind === 'stem' ? pillar.stem_element : pillar.branch_element
  const tenGod = kind === 'stem' ? pillar.stem_ten_god : pillar.branch_ten_god
  const color = ohaengVar(element)
  const border = isDay ? 'border-[1.5px] border-c-text' : 'border border-c-line'
  return (
    <div className={`flex-1 rounded-2xl ${border} px-1 py-2 text-center`}
      style={{ background: ohaengTintVar(element) }}>
      {label && (
        <p className={`text-[10px] ${isDay ? 'font-extrabold text-c-text' : 'font-bold text-c-text-sub'}`}>
          {label}{isDay ? ' ★' : ''}
        </p>
      )}
      <p className="font-serif text-[26px] font-black leading-tight" style={{ color }}>{hanja}</p>
      <p className="text-[11px] font-extrabold" style={{ color }}>{kor} · {element}</p>
      <p className="mt-0.5 text-[10px] text-c-text-sub">{tenGod}</p>
    </div>
  )
}
